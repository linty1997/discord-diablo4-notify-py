import { handleScheduled } from './scheduledTask.js';
import { hono_app } from './app.js';

addEventListener('fetch', event => {
    event.respondWith(hono_app.handleEvent(event))
})

addEventListener('scheduled', event => {
    event.waitUntil(handleScheduled(event, KV))
})