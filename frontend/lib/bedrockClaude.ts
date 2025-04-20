import { BedrockRuntimeClient, InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";

const bedrock = new BedrockRuntimeClient({
  region: "us-east-1",
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export async function sendToClaude(prompt: string): Promise<string> {
  const payload = {
    anthropic_version: "bedrock-2023-05-31",
    max_tokens: 1000,
    temperature: 0.7,
    messages: [
      { role: "user", content: prompt }
    ],
  };

  const command = new InvokeModelCommand({
    modelId: "anthropic.claude-3-sonnet-20240229-v1:0",
    body: JSON.stringify(payload),
    contentType: "application/json",
    accept: "application/json",
  });

  const response = await bedrock.send(command);
  const responseBody = response.body.transformToString();
  const parsed = JSON.parse(responseBody);
  return parsed.content[0].text;
}
