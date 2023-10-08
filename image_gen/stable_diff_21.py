from gradio_client import Client

client = Client("https://jingyechen22-textdiffuser.hf.space/")

def prototype1_imagegen(prompt="A cat", sampling_step=20, model="Stable Diffusion v1.5", scfg=7.5, batch=1):
    if model == "Stable Diffusion v2.1":
        batch = 1
    result = client.predict(
        prompt,
        sampling_step,
        scfg,
        batch,
        model,
        fn_index=1
    )
    print(result)
    return result
    # NOTE: The image is returned as a base64 string, so you will need to decode it before using