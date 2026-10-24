import asyncio
import os
import sys
from dotenv import load_dotenv
import websockets

load_dotenv(".env")

POOLED_PORT = 5432
UNPOOLED_PORT = 54320
POOLED_HOST = "ep-sweet-rain-b5ncitxd-pooler.c-7.us-east-2.aws.neon.tech"
UNPOOLED_HOST = "ep-sweet-rain-b5ncitxd.c-7.us-east-2.aws.neon.tech"

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, target_host: str):
    ws_url = f"wss://{target_host}/v2"
    try:
        async with websockets.connect(ws_url, subprotocols=["binary"]) as ws:
            async def tcp_to_ws():
                try:
                    while True:
                        data = await reader.read(16384)
                        if not data:
                            break
                        await ws.send(data)
                except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
                    pass

            async def ws_to_tcp():
                try:
                    async for msg in ws:
                        if isinstance(msg, str):
                            msg = msg.encode("utf-8")
                        tcp_writer_write(writer, msg)
                        await writer.drain()
                except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
                    pass

            def tcp_writer_write(w, d):
                w.write(d)

            done, pending = await asyncio.wait(
                [asyncio.create_task(tcp_to_ws()), asyncio.create_task(ws_to_tcp())],
                return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
    except Exception as e:
        print(f"[NeonProxy] WS error ({target_host}): {e}", flush=True)
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

async def main():
    async def handler_pooled(r, w):
        await handle_client(r, w, POOLED_HOST)

    async def handler_unpooled(r, w):
        await handle_client(r, w, UNPOOLED_HOST)

    srv_pooled = await asyncio.start_server(handler_pooled, "127.0.0.1", POOLED_PORT)
    srv_unpooled = await asyncio.start_server(handler_unpooled, "127.0.0.1", UNPOOLED_PORT)

    print(f"[NeonProxy] Ready!", flush=True)
    print(f"  - 127.0.0.1:{POOLED_PORT} -> wss://{POOLED_HOST}/v2 (pooled)", flush=True)
    print(f"  - 127.0.0.1:{UNPOOLED_PORT} -> wss://{UNPOOLED_HOST}/v2 (unpooled)", flush=True)

    async with srv_pooled, srv_unpooled:
        await asyncio.gather(srv_pooled.serve_forever(), srv_unpooled.serve_forever())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
