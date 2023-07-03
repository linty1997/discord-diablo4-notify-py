export async function set_kv(kv, key, value) {
    const kv_data = await get_kv(kv)
    kv_data[key] = value
    await kv.put("line_user_settings", JSON.stringify(kv_data))
    console.log(`更新 ${key} 設定: ${value}`)
}

export async function get_kv(kv) {
    const result = await kv.get("line_user_settings");
    return JSON.parse(result);
}

export async function get_line_data_kv(kv) {
    return JSON.parse(await kv.get('line_push_data'))
}

export async function set_line_data_kv(kv, event, push_time=null) {
    const line_data = await get_line_data_kv(kv)
    if (push_time){
        line_data[event].push_time = push_time
    }
    line_data[event].status = true
    await kv.put('line_push_data', JSON.stringify(line_data))
    console.log(`更新 ${event} 推播時間: ${push_time}`)
}

