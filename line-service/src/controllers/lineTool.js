import {get_kv, set_line_data_kv} from "./kvTool.js"

export class LineTool {
    constructor(KV) {
        this.world_boss_notify_interval = 4  // 通知間隔(時間單位: 小時)
        this.hell_tide_notify_interval = 1  // 通知間隔(時間單位: 小時)
        this.line_notify_url = 'https://notify-api.line.me/api/notify'
        this.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        this.kv = KV
    }

    async check_push_time(event, data) {
        if (event === 'legions') {  // 軍團戰暫不推播
            return
        }
        const now_timestamp = Math.floor(Date.now() / 1000)
        const event_time = data.event_time
        const push_time = data.push_time
        const name = data.name
        const location = data.location
        const status = data.status
        const cd = (event === 'hell_tide') ? this.hell_tide_notify_interval : this.world_boss_notify_interval
        if (event_time > push_time && (event_time - push_time) > cd * 3600 && status === false && now_timestamp - push_time > 180) {  // 推播
            const message = await this.get_push_message(event, event_time, name, location)
            const line_notify_data = await get_kv(this.kv)
            await set_line_data_kv(this.kv, event, now_timestamp)  // 更新推送時間
            for (let [user_id, token] of Object.entries(line_notify_data)) {  // 推播
                try {
                    const res = await this.push_line_notify(token, message)
                    console.log(`user_id: ${user_id}, Token: ${token}, 狀態: ${res}`)
                } catch (e) {
                    console.log(`user_id: ${user_id}, Token: ${token}, 錯誤: ${e}`)
                }
            }
        }
        // 測試地獄浪潮前五分鐘通知
        const next_event_start_time = event_time + (60 * 60 + 15 * 60)
        if (event === 'hell_tide' && now_timestamp > (next_event_start_time - (3 * 60)) && now_timestamp < next_event_start_time && status === false) {
            const end_time = next_event_start_time + 3600
            const message = await this.get_push_message_hell_tide(event, end_time)
            const line_notify_data = await get_kv(this.kv)
            await set_line_data_kv(this.kv, event)  // 更新推送狀態
            for (let [user_id, token] of Object.entries(line_notify_data)) {  // 推播
                try {
                    const res = await this.push_line_notify(token, message)
                    console.log(`提前通知成功, user_id: ${user_id}, Token: ${token}, 狀態: ${res}`)
                } catch (e) {
                    console.log(`提前通知失敗, user_id: ${user_id}, Token: ${token}, 錯誤: ${e}`)
                }
            }
        }
    }

    async get_push_message(event, event_time, name=null, location=null) {
        const str_time = await this.get_str_time(event_time)
        let message = ''
        const event_name = (event === 'hell_tide') ? '地獄浪潮' : '世界王'
        if (event === 'world_boss') {
            message = `${event_name}\n刷新時間(UTC+8): ${str_time}\n名稱: ${name}`
        } else {
            message = `${event_name}\n結束時間(UTC+8): ${str_time}\n位置: ${location}`
        }
        return message
    }

    async get_push_message_hell_tide(event, end_time) {
        const str_time = await this.get_str_time(end_time)
        return`地獄浪潮\n預計三分鐘後開始\n結束時間(UTC+8): ${str_time}`

    }

    async push_line_notify(token, message) {
        this.headers["Authorization"] = "Bearer " + token
        const payload = new URLSearchParams({
            'message': message
        })
        const response = await fetch(this.line_notify_url, {
            method: 'POST',
            headers: this.headers,
            body: payload
        })
        return response.status
    }

    async get_str_time(timestamp) {
        let date = new Date(timestamp * 1000);
        let dateString = date.toLocaleDateString('zh-TW', {timeZone: 'Asia/Taipei', month: '2-digit', day: '2-digit'})
        let timeString = date.toLocaleTimeString('zh-TW', {
            timeZone: 'Asia/Taipei',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        })
        return `${dateString} ${timeString}`
    }

}
