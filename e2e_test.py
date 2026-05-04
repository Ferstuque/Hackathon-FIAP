import httpx
import asyncio
import time
import os

API_URL = "http://localhost:8000/api/v1"

async def test_end_to_end():
    print("🚀 Iniciando Teste E2E - Architecture Analyzer...")
    
    # 1. Cria uma "imagem" fake para teste
    fake_image_path = "test_diagram.jpg"
    with open(fake_image_path, "wb") as f:
        f.write(b"fake image content")
        
    try:
        async with httpx.AsyncClient() as client:
            # --- UPLOAD ---
            print("\n➡️  Enviando Imagem (POST /upload)...")
            with open(fake_image_path, "rb") as f:
                upload_res = await client.post(
                    f"{API_URL}/upload", 
                    files={"file": (fake_image_path, f, "image/jpeg")}
                )
            
            if upload_res.status_code != 201:
                print(f"❌ Erro no upload: {upload_res.status_code} - {upload_res.text}")
                return
                
            process_id = upload_res.json()["id"]
            print(f"✅ Recebido! Processo ID: {process_id}")
            
            # --- STATUS POLLING ---
            print("\n➡️  Aguardando Processamento da IA (GET /status)...")
            max_attempts = 15
            for i in range(max_attempts):
                status_res = await client.get(f"{API_URL}/status/{process_id}")
                if status_res.status_code == 200:
                    current_status = status_res.json()["status"]
                    print(f"   Status atual: {current_status}")
                    
                    if current_status == "ANALISADO":
                        print("   Processamento concluído. Aguardando propagação dos dados no DB...")
                        await asyncio.sleep(2)
                        break
                    elif current_status == "ERRO":
                        print("❌ O processamento falhou na IA.")
                        return
                await asyncio.sleep(3)
            
            # --- GET REPORT ---
            print("\n➡️  Buscando Relatório Final (GET /report)...")
            for i in range(10):
                report_res = await client.get(f"{API_URL}/report/{process_id}")
                if report_res.status_code == 200:
                    print("\n✅ Relatório Gerado com Sucesso! 📊")
                    print("="*40)
                    import json
                    print(json.dumps(report_res.json(), indent=2, ensure_ascii=False))
                    print("="*40)
                    return
                print("   Relatório não encontrado ainda, aguardando...")
                await asyncio.sleep(2)
            
            print(f"❌ Erro ao buscar relatório ou Timeout: {report_res.status_code} - {report_res.text}")

    finally:
        # Cleanup
        if os.path.exists(fake_image_path):
            os.remove(fake_image_path)

if __name__ == "__main__":
    asyncio.run(test_end_to_end())