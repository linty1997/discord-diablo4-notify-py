import { Hono } from 'hono'
import { set_kv } from "./controllers/kvTool.js"

const app = new Hono()

app.get('/', (c) => {
    return c.text('Hello!')
})

app.post('/', async (c) => {
    try {
        const body = await c.req.parseBody()
        if (body.code != null && body.state != null) {
            const code = body.code
            const state = body.state
            const params = new URLSearchParams()
            params.append('grant_type', 'authorization_code')
            params.append('code', code)
            params.append('redirect_uri', REDIRECT_URL)
            params.append('client_id', LINE_NOTIFY_CLIENT_ID)
            params.append('client_secret', LINE_NOTIFY_CLIENT_SECRET)

            const res = await fetch('https://notify-bot.line.me/oauth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: params
            })
            const resData = await res.json()
            if (resData.status === 200) {
                const token = resData.access_token
                const res = await set_kv(KV, state, token)
            } else {
                return c.text('取得 Token 失敗!')
            }
        }
        return c.text('已成功連結 Line Notify!')
    } catch (e) {
        console.log(e)
        return c.text('Error!')
    }
})

export const hono_app = app