import flet as ft
import google.generativeai as genai
import tempfile
import os
from docx import Document
from docx.shared import Inches
import markdown
from io import BytesIO
from dotenv import load_dotenv

API_KEY = os.getenv('APIKEY')
genai.configure(api_key=API_KEY)

def generate_api(issue, features, type_job="Trabajo de investigacion"):
    
        
    try:
        
        HUMANIZADOR = "Cuando se trata de escribir contenido, dos factores son cruciales: la \"perplejidad\" y la \"explosividad\". La perplejidad mide la complejidad del texto. Por separado, la explosividad compara las variaciones de las oraciones. Los seres humanos tienden a escribir con mayor explosividad, por ejemplo, combinando algunas oraciones más largas o complejas con otras más cortas. Las oraciones generadas por la inteligencia artificial suelen ser más uniformes. Por lo tanto, al escribir el siguiente contenido, voy a pedirte que lo crees con un buen grado de perplejidad y explosividad. Utilizando los conceptos mencionados anteriormente, reescribe este texto con un alto nivel de perplejidad y explosividad sin alargarlo demasiado, pero tampoco con mucha brevedad: "
        

        

        feature_list = features.split(",")
        responses = []
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        total = ""
        #response = model.generate_content(, stream=True)
        for feature in feature_list:
            prompt =  f"Dame el {feature} y solo el {feature}(si crees que es muy corta puedes alargarla un poco) de {issue}"
            text_request = model.generate_content(prompt).text
            response_text = model.generate_content(HUMANIZADOR + text_request).text
            total += response_text
            issue_response = {"issue": issue, "feature": feature, "response": response_text}
            responses.append(issue_response)
        introduccion = model.generate_content(HUMANIZADOR + f"Quiero que me generes la Introduccion de este {type_job}: {total}").text
        introduccion = model.generate_content(HUMANIZADOR + introduccion).text
        total = introduccion + total
        conclusion = model.generate_content(HUMANIZADOR + f"Quiero que me generes la conclusion de este {type_job}: {total}").text
        conclusion = model.generate_content(HUMANIZADOR + conclusion).text
        introduccion_response = {"issue": issue, "feature": "introduccion", "response": introduccion}
        conclusion_response = {"issue": issue, "feature": "conclusion", "response": conclusion}
        responses.append(conclusion_response)
        responses.insert(0,introduccion_response)
        response = responses
         
        print(response)
        return response
        
        
    except Exception as e:
        return "An error"
def markdown_to_docx(markdown_text):
    # Convertir Markdown a HTML
    html = markdown.markdown(markdown_text)
    
    # Crear un nuevo documento Word
    doc = Document()
    
    # Añadir el contenido HTML al documento
    doc.add_paragraph(html)
    
    # Guardar el documento en un BytesIO object
    f = BytesIO()
    doc.save(f)
    f.seek(0)
    return f

def main(page: ft.Page):
    page.title = "Proyecto Académico Libre"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def generate_project(e):
        issue = topic_input.value
        features = project_characteristics.value if not auto_generate.value else "introducción,desarrollo,conclusión"
        type_job = job_type.value

        loading.visible = True
        page.update()

        result = generate_api(issue, features, type_job)

        loading.visible = False

        global markdown_content
        markdown_content = ""
        for item in result:
            markdown_content += f"## {item['feature'].capitalize()}\n\n{item['response']}\n\n---\n\n"
        
        output.value = markdown_content
        result_container.visible = True
        page.update()

    def download_docx(e):
        docx_file = markdown_to_docx(markdown_content)
        
        temp_dir = tempfile.gettempdir()
        file_name = os.path.join(temp_dir, "proyecto_academico.docx")
        
        with open(file_name, "wb") as f:
            f.write(docx_file.getvalue())
        
        page.launch_url(file_name)

    title = ft.Text("La forma más inteligente de lograr el éxito académico", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    subtitle = ft.Text("un trabajo académico", size=24, italic=True, text_align=ft.TextAlign.CENTER)
    description = ft.Text("Aprende, crea y edita con facilidad — ahorra tiempo para lo que importa", size=16, text_align=ft.TextAlign.CENTER)

    topic_input = ft.TextField(width=400, height=50, border_radius=25, label="Tema del proyecto")
    job_type = ft.Dropdown(
        width=400,
        options=[
            ft.dropdown.Option("Trabajo de investigacion"),
            ft.dropdown.Option("Ensayo"),
            ft.dropdown.Option("Artículo científico"),
        ],
        label="Tipo de trabajo"
    )

    auto_generate = ft.Checkbox(label="Dejar que la aplicación decida las características", value=False)
    project_characteristics = ft.TextField(width=400, height=100, multiline=True, label="Características del proyecto (separadas por comas)")

    generate_button = ft.ElevatedButton("Generar proyecto", on_click=generate_project)
    download_button = ft.ElevatedButton("Descargar como Word", on_click=download_docx)

    loading = ft.ProgressRing(visible=False)

    output = ft.Markdown("", selectable=True)
    output_container = ft.Container(
        content=ft.Column([output], scroll=ft.ScrollMode.ALWAYS),
        width=600,
        height=400,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=10,
        padding=10,
    )

    result_container = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("Resultado del proyecto", style=ft.TextThemeStyle.HEADLINE_SMALL),
                download_button
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            output_container
        ]),
        width=620,
        visible=False
    )

    page.add(
        ft.Column([
            title,
            subtitle,
            description,
            ft.Container(height=20),
            topic_input,
            job_type,
            ft.Container(height=20),
            auto_generate,
            project_characteristics,
            generate_button,
            loading,
            result_container
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

ft.app(target=main)