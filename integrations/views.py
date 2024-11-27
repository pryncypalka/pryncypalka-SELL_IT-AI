from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv
from django.views import View
from django.http import JsonResponse
import json

load_dotenv()

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.getenv("OPENAI_KEY", None),
)


class ChatGPTView(View):
    def post(self, request):
        prompt = request.POST.get("prompt")

        if not prompt:
            return JsonResponse({"error": "Prompt is required"})
        
        try:
            response = client.chat.completions.create(
                messages=[
                {
                    "role": "user",
                    "content": "Say this is a test",
                }
                ],
                model="gpt-3.5-turbo",
            )
            message = response.choices[0].text.strip()
            return JsonResponse({"message": message})
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
                
           