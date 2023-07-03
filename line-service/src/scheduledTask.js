import { get_line_data_kv } from "./controllers/kvTool.js"
import { LineTool } from "./controllers/lineTool.js"

export async function handleScheduled(event, kv) {
    const data = await get_line_data_kv(kv)
    for (let event in data) {
        if (data.hasOwnProperty(event)) {
            let value = data[event]
            const lineToolInstance = new LineTool(kv)
            await lineToolInstance.check_push_time(event, value)
        }
    }
}
