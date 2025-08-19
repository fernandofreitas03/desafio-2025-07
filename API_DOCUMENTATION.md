### 📝 API de Formatação de Texto

### 📌 Descrição
Esta API recebe um texto, quebra em linhas com largura máxima definida e pode aplicar ou não **justificação**.  
Retorna o texto formatado como **string** e também como lista de linhas.

---

## 🚀 Endpoints

### **POST `/format`**
Formata um texto com base na largura e na configuração de justificação.

#### **Parâmetros (JSON Body)**

| Campo      | Tipo      | Obrigatório | Descrição |
|------------|-----------|-------------|-----------|
| `text`     | string    | ✅          | Texto a ser formatado |
| `width`    | inteiro   | ✅          | Quantidade máxima de caracteres por linha |
| `justify`  | booleano  | ❌          | Se `true`, aplica justificação (espaços distribuídos). Padrão: `false` |

---

#### **Exemplo de requisição**
```bash
curl -X POST "http://127.0.0.1:3000/format" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "width": 40,
    "justify": false
  }'
```

---

#### **Exemplo de resposta**

```json
{
  "formatted": "Lorem ipsum dolor sit amet, consectetur\nadipiscing elit.",
  "lines": [
    "Lorem ipsum dolor sit amet, consectetur",
    "adipiscing elit."
  ]
}
```

---

## 🛠 Rodando Localmente (sem Docker)

1. **Instalar dependências**

```bash
pip install -r requirements.txt
```

2. **Rodar servidor**

```bash
uvicorn app:app --host 0.0.0.0 --port 3000
```

3. **Testar com cURL**

```bash
curl -X POST "http://127.0.0.1:3000/format" \
  -H "Content-Type: application/json" \
  -d '{"text": "Seu texto aqui", "width": 50, "justify": true}'
```

---

## 🐳 Rodando com Docker

### **1. Build da imagem**

```bash
docker build -t format-api .
```

### **2. Rodar container**

```bash
docker run -d -p 3000:3000 format-api
```

### **3. Testar**

```bash
curl -X POST "http://127.0.0.1:3000/format" \
  -H "Content-Type: application/json" \
  -d '{"text": "Texto de exemplo", "width": 50, "justify": false}'
```

---

## 🧪 Testando no Postman

1. Abra o **Postman**.
2. Crie uma **nova requisição**:

   * Método: `POST`
   * URL: `http://127.0.0.1:3000/format`
3. Vá em **Body → raw → JSON** e insira:

```json
{
  "text": "Texto de exemplo para formatação",
  "width": 40,
  "justify": true
}
```

4. Clique em **Send**.

---

## 🔎 Resumo das respostas possíveis

| Situação                  | Código HTTP | Resposta                                   |
| ------------------------- | ----------- | ------------------------------------------ |
| Sucesso                   | 200         | JSON com texto formatado e lista de linhas |
| Campo obrigatório ausente | 422         | Erro de validação                          |
| Erro interno no servidor  | 500         | Mensagem de erro genérica                  |

