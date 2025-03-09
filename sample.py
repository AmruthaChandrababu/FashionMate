import requests
import json

url = "https://stablediffusionapi.com/api/v5/fashion"

payload = json.dumps({
   "key": "",
   "prompt": "A realistic photo of a model wearing a beautiful white top.",
   "negative_prompt": "Low quality, unrealistic, bad cloth, warped cloth",
   "init_image": "https://www.vstar.in/media/cache/350x0/catalog/product/f/0/f09632_parent_1_1653003388.jpg",
   "cloth_image": "https://thumbs.dreamstime.com/b/plain-hollow-female-tank-top-shirt-isolated-white-background-30020169.jpg",
   "cloth_type": "upper_body",
   "height": 512,
   "width": 384,
   "guidance_scale": 8.0,
   "num_inference_steps": 20,
   "seed": 128915590,
   "temp": "no",
   "webhook": None,
   "track_id": None 
})

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)