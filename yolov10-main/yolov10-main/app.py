import gradio as gr
import cv2
import tempfile
from ultralytics import YOLOv10

def yolov10_inference(image, video, model_id, image_size, conf_threshold):
    # 加载模型
   # model = YOLO(f'{model_id}') if model_id != "best.pt" else YOLO("best.pt")
    model = YOLOv10(r'./best.pt')
    device = "cpu"  # 强制使用CPU

    # 图像推理
    if image:
        print(type(image))
        print(image)
        print(112321)
        results = model.predict(source=image, imgsz=image_size, conf=conf_threshold, device=device)
        annotated_image = results[0].plot()

        # 提取类别信息
        class_name = None
        detected_classes = []
        for result in results[0].boxes:
            class_id = result.cls.item()  # 将 tensor 转换为整数
            class_name = model.names[class_id]


        if class_name is not None:
            return annotated_image[:, :, ::-1], class_name  # 返回标注的图像，OpenCV格式
        else:
            return annotated_image, None



    # 视频推理
    else:
        video_path = tempfile.mktemp(suffix=".webm")
        with open(video, "rb") as f:
            with open(video_path, "wb") as g:
                g.write(f.read())

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_video_path = tempfile.mktemp(suffix=".webm")
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'vp80'), fps, (frame_width, frame_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model.predict(source=frame, imgsz=image_size, conf=conf_threshold, device=device)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        cap.release()
        out.release()

        interface.launch(show_error=True, share=True)
        return None, output_video_path  # 返回标注的视频路径






def yolov10_inference_for_examples(image, model_path, image_size, conf_threshold):
    annotated_image, _ = yolov10_inference(image, None, model_path, image_size, conf_threshold)
    return annotated_image


def app():
    with gr.Blocks():
        with gr.Row():
            with gr.Column():
                image = gr.Image(type="pil", label="Image", visible=True)
                video = gr.Video(label="Video", visible=False)
                input_type = gr.Radio(
                    choices=["Image", "Video"],
                    value="Image",
                    label="Input Type",
                )
                model_id = gr.Dropdown(
                    label="Model",
                    choices=[
                        "yolov10n",
                        "yolov10s",
                        "yolov10m",
                        "yolov10b",
                        "yolov10l",
                        "yolov10x",
                        "best.pt"
                    ],
                    value="best.pt",
                )
                image_size = gr.Slider(
                    label="Image Size",
                    minimum=320,
                    maximum=1280,
                    step=32,
                    value=640,
                )
                conf_threshold = gr.Slider(
                    label="Confidence Threshold",
                    minimum=0.0,
                    maximum=1.0,
                    step=0.05,
                    value=0.25,
                )
                yolov10_infer = gr.Button(value="Detect Objects")

            with gr.Column():
                output_image = gr.Image(type="numpy", label="Annotated Image", visible=True)
                output_video = gr.Textbox(label="Annotated Video", visible=False)







        def update_visibility(input_type):
            image_vis = gr.update(visible=True) if input_type == "Image" else gr.update(visible=False)
            video_vis = gr.update(visible=False) if input_type == "Image" else gr.update(visible=True)
            output_image_vis = gr.update(visible=True) if input_type == "Image" else gr.update(visible=False)
            output_video_vis = gr.update(visible=False) if input_type == "Image" else gr.update(visible=True)

            return image_vis, video_vis, output_image_vis, output_video_vis

        input_type.change(
            fn=update_visibility,
            inputs=[input_type],
            outputs=[image, video, output_image, output_video],
        )

        def run_inference(image, video, model_id, image_size, conf_threshold, input_type):
            if input_type == "Image":
                return yolov10_inference(image, None, model_id, image_size, conf_threshold)
            else:
                return yolov10_inference(None, video, model_id, image_size, conf_threshold)


        yolov10_infer.click(
            fn=run_inference,
            inputs=[image, video, model_id, image_size, conf_threshold, input_type],
            outputs=[output_image, output_video],
        )

        gr.Examples(
            examples=[
                [
                    "ultralytics/assets/bus.jpg",
                    "yolov10s",
                    640,
                    0.25,
                ],
                [
                    "ultralytics/assets/zidane.jpg",
                    "yolov10s",
                    640,
                    0.25,
                ],
            ],
            fn=yolov10_inference_for_examples,
            inputs=[
                image,
                model_id,
                image_size,
                conf_threshold,
            ],
            outputs=[output_image],
            cache_examples='lazy',
        )


gradio_app = gr.Blocks()
with gradio_app:
    gr.HTML(
        """
        <h1 style='text-align: center'>YOLOv10: Real-Time End-to-End Object Detection</h1>
        """
    )
    gr.HTML(
        """
        <h3 style='text-align: center'>
        <a href='https://arxiv.org/abs/2405.14458' target='_blank'>arXiv</a> | <a href='https://github.com/THU-MIG/yolov10' target='_blank'>github</a>
        </h3>
        """
    )
    with gr.Row():
        with gr.Column():
            app()

if __name__ == '__main__':
    gradio_app.launch(share=True,show_error=True)


