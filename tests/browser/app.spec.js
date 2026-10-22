'use strict';
const {test, expect} = require('@playwright/test');
const KEY = 'legacy-tv-hub.v1';

async function seed(page, items) {
    await page.goto('/');
    await page.evaluate(({key, items}) => localStorage.setItem(key, JSON.stringify({version: 1, items, contrast: false})), {key: KEY, items});
    await page.reload();
}
async function saved(page) {
    return page.evaluate(key => JSON.parse(localStorage.getItem(key)), KEY);
}

test('remote navigation, full video, pause/resume and return home', async ({page}) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('/');
    await expect(page.getByRole('button', {name: /Play a video/})).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.locator('#url-input')).toBeFocused();
    await page.keyboard.press('Escape');
    await page.getByRole('button', {name: /Play the demo/}).click();
    await expect.poll(() => page.locator('#video').evaluate(v => v.currentTime)).toBeGreaterThan(0.3);
    await page.keyboard.press('Space');
    await expect.poll(() => page.locator('#video').evaluate(v => v.paused)).toBe(true);
    const paused = await page.locator('#video').evaluate(v => v.currentTime);
    await page.waitForTimeout(250);
    expect(await page.locator('#video').evaluate(v => v.currentTime)).toBeCloseTo(paused, 1);
    await page.keyboard.press('ArrowDown');
    await expect(page.getByRole('button', {name: 'Play / pause', exact: true})).toBeFocused();
    await page.keyboard.press('Enter');
    await expect.poll(() => page.locator('#video').evaluate(v => v.ended), {timeout: 15000}).toBe(true);
    await expect(page.locator('#player-state')).toHaveText('Finished');
    await page.keyboard.press('Escape');
    await expect(page.locator('#player-screen')).toBeHidden();
    await expect(page.getByRole('button', {name: /Play a video/})).toBeFocused();
    expect(errors).toEqual([]);
});

test('home page clearly describes browser-only scope and opens compatibility details', async ({page}) => {
    await page.goto('/');
    await expect(page.getByText('BROWSER APP', {exact: true})).toBeVisible();
    await expect(page.getByText(/does not replace Smart Hub or add streaming services/i)).toBeVisible();
    await expect(page.getByRole('button', {name: /Play the demo/})).toBeInViewport();
    await expect(page.getByRole('button', {name: /TV & app support/})).toBeInViewport();
    await expect(page.locator('footer')).toBeInViewport();
    await page.getByRole('button', {name: /TV & app support/}).click();
    await expect(page.getByRole('heading', {name: 'TV & app support'})).toBeVisible();
    await expect(page.getByText(/does not replace Smart Hub, update the TV, or provide Paramount\+/i)).toBeVisible();
    await expect(page.getByText(/Survival across a TV power cycle is unverified/i)).toBeVisible();
});

test('closing before metadata preserves the existing resume point', async ({page, baseURL}) => {
    let release;
    const gate = new Promise(resolve => { release = resolve; });
    await page.route('**/slow.mp4', async route => { await gate; await route.abort(); });
    await seed(page, [{title: 'Waiting video', url: baseURL + '/slow.mp4', position: 45, duration: 120, played: 1}]);
    await page.getByRole('button', {name: /My videos/}).click();
    await page.getByRole('button', {name: 'Resume', exact: true}).click();
    await expect(page.locator('#player-state')).toHaveText(/^(Loading|Buffering)…$/);
    await page.keyboard.press('Escape');
    const item = (await saved(page)).items[0];
    expect(item.position).toBe(45);
    expect(item.duration).toBe(120);
    release();
});

test('editing a source resets its history and rejects duplicate links atomically', async ({page, baseURL}) => {
    await seed(page, [
        {title: 'First', url: baseURL + '/first.mp4', position: 45, duration: 120, played: 1},
        {title: 'Second', url: baseURL + '/second.mp4', position: 30, duration: 80, played: 2}
    ]);
    await page.getByRole('button', {name: /My videos/}).click();
    await page.getByRole('button', {name: 'Edit', exact: true}).first().click();
    await page.locator('#title-input').fill('Renamed');
    await page.getByRole('button', {name: 'Save', exact: true}).click();
    expect((await saved(page)).items[0].position).toBe(45);
    await page.getByRole('button', {name: 'Edit', exact: true}).first().click();
    await page.locator('#url-input').fill(baseURL + '/second.mp4');
    await page.getByRole('button', {name: 'Save', exact: true}).click();
    await expect(page.locator('#editor-error')).toHaveText('A video with that link is already saved.');
    expect((await saved(page)).items[0].url).toBe(baseURL + '/first.mp4');
    await page.locator('#url-input').fill(baseURL + '/replacement.mp4');
    await page.getByRole('button', {name: 'Save', exact: true}).click();
    const item = (await saved(page)).items[0];
    expect([item.position, item.duration, item.played]).toEqual([0, 0, 0]);
});

test('a damaged library can be saved again and video errors remain escapable', async ({page, baseURL}) => {
    await page.goto('/');
    await page.evaluate(key => localStorage.setItem(key, '{broken'), KEY);
    await page.reload();
    await expect(page.locator('#notice')).toContainText('Unreadable saved library');
    await page.getByRole('button', {name: /Play a video/}).click();
    await page.locator('#title-input').fill('<Test video>');
    await page.locator('#url-input').fill(baseURL + '/missing.mp4');
    await page.getByRole('button', {name: 'Save & play', exact: true}).click();
    await expect(page.locator('#player-state')).toContainText('Cannot play this link');
    await page.keyboard.press('Escape');
    await page.reload();
    await page.getByRole('button', {name: /My videos/}).click();
    await expect(page.locator('.video-copy h2')).toHaveText('<Test video>');
    expect((await saved(page)).items).toHaveLength(1);
});
