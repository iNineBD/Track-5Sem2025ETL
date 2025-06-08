import asyncio
from prefect.client.orchestration import get_client

async def delete_all_flow_runs():
    async with get_client() as client:
        print("Buscando flow runs...")
        flow_runs = await client.read_flow_runs()
        
        if not flow_runs:
            print("Nenhum flow run encontrado.")
            return

        for run in flow_runs:
            print(f"Deletando flow run: {run.id}")
            await client.delete_flow_run(run.id)

        print("Todos os flow runs foram deletados com sucesso.")

if __name__ == "__main__":
    asyncio.run(delete_all_flow_runs())