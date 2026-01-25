import asyncio
import os
import signal

from src.presentation.grpc import create_grpc_server


async def serve() -> None:
    host = os.getenv("GRPC_HOST", "0.0.0.0")
    port = int(os.getenv("GRPC_PORT", "50051"))

    server = await create_grpc_server()
    server.add_insecure_port(f"{host}:{port}")

    await server.start()
    print(f"[gRPC] server started on {host}:{port}")

    stop_event = asyncio.Event()

    def _graceful_shutdown(*_):
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _graceful_shutdown)
        except NotImplementedError:
            # Windows
            pass

    await stop_event.wait()
    print("[gRPC] shutting down...")
    await server.stop(grace=5)


def main() -> None:
    asyncio.run(serve())


if __name__ == "__main__":
    main()
