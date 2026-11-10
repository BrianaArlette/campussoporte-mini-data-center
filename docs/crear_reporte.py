"""Genera el documento Word editable del proyecto (sin evidencia ficticia)."""
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import RGBColor
from pathlib import Path

out=Path(__file__).resolve().parent/'Reporte_CampusSoporte_Editable.docx'
doc=Document();sec=doc.sections[0];sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.8);sec.left_margin=Inches(.87);sec.right_margin=Inches(.87)
style=doc.styles['Normal'];style.font.name='Times New Roman';style.font.size=Pt(12);style.font.color.rgb=RGBColor(0,0,0);style.paragraph_format.space_after=Pt(6)
for n in ['Title','Heading 1','Heading 2']:
 st=doc.styles[n];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
 st.font.bold=True
 st.font.size=Pt(14 if n=='Title' else 12)
 st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(6)

def encabezado(title):
 p=doc.add_paragraph();p.paragraph_format.space_before=Pt(12);p.paragraph_format.space_after=Pt(5)
 r=p.add_run(title);r.bold=True;r.font.name='Times New Roman';r.font.size=Pt(12);r.font.color.rgb=RGBColor(0,0,0)
 return p

def section(title,txt):
 encabezado(title)
 doc.add_paragraph(txt)
def para(bold,text):
 p=doc.add_paragraph();r=p.add_run(bold);r.bold=True;p.add_run(text)
 return p

def blank(tag):
 p=doc.add_paragraph('['+tag+']');p.paragraph_format.space_after=Pt(13);return p

title=doc.add_paragraph();title.alignment=WD_ALIGN_PARAGRAPH.CENTER;rr=title.add_run('CampusSoporte: Mini Centro de Datos con Docker');rr.bold=True;rr.font.name='Times New Roman';rr.font.size=Pt(14);rr.font.color.rgb=RGBColor(0,0,0)
section('Objetivo del proyecto','Diseñar e implementar un mini centro de datos virtual mediante Docker Compose para ejecutar una aplicación de reportes tecnológicos, distribuir solicitudes entre varios servidores web, almacenar registros de forma persistente y observar el funcionamiento de los servicios.')
section('Problema que atiende','En un entorno universitario, los problemas de conectividad, computadoras, proyectores y plataformas digitales pueden dificultar las actividades. Como ejercicio académico se desarrolló CampusSoporte, una aplicación local que permite registrar incidencias y consultar su estado. El sistema no representa un servicio oficial de la universidad y los registros de ejemplo son ficticios.')
section('Arquitectura propuesta','Se utilizó Docker Compose para definir diez servicios relacionados. Un balanceador Nginx recibe peticiones en el puerto 8080 y las distribuye entre tres contenedores web (web1, web2 y web3). Una API Python procesa los reportes y se conecta a MariaDB. Grafana consulta la base de datos y los registros de acceso que Alloy recolecta para Loki. Portainer permite administrar los contenedores desde una interfaz gráfica.')
section('Funciones de la aplicación','La aplicación permite registrar un reporte con título, categoría, ubicación, prioridad y descripción; consultar las incidencias y filtrarlas; modificar sus datos y estado; eliminarlas; y consultar contadores por estado. También contiene un laboratorio que envía solicitudes al balanceador y muestra qué nodo las atendió.')
section('Tecnologías utilizadas','Docker Desktop, Docker Compose, Nginx, Python, MariaDB, Grafana, Loki, Alloy, Portainer, HTML, CSS, JavaScript y PowerShell.')
encabezado('Pruebas y resultados')
doc.add_paragraph('Completar esta sección únicamente después de ejecutar las pruebas reales en la computadora. No agregar resultados simulados como si fueran observados.')
table=doc.add_table(rows=1,cols=3);table.style='Table Grid';table.alignment=WD_TABLE_ALIGNMENT.CENTER
for cell,txt in zip(table.rows[0].cells,['Prueba','Qué se debe comprobar','Resultado real']):cell.text=txt
for values in [
 ('Despliegue','Contenedores activos y puertos correctos','[Pendiente de verificar]'),
 ('Registro CRUD','Crear, consultar, modificar y eliminar un reporte','[Pendiente de verificar]'),
 ('Balanceo','Distribución de 30 solicitudes entre web1, web2 y web3','web1=[ ]; web2=[ ]; web3=[ ]; fallos=[ ]'),
 ('Persistencia','Reportes conservados después de docker compose down/up','[Pendiente de verificar]'),
 ('Alta disponibilidad','Continuidad del servicio con web2 detenido','[Pendiente de verificar]'),
 ('Monitoreo','Consultas y logs visibles en Grafana','[Pendiente de verificar]')
]:
 row=table.add_row();
 for c,v in zip(row.cells,values): c.text=v
for row in table.rows:
 trPr=row._tr.get_or_add_trPr();flag=OxmlElement('w:cantSplit');trPr.append(flag)
 for c in row.cells:
  for p in c.paragraphs:
   for r in p.runs:r.font.size=Pt(10.5);r.font.color.rgb=RGBColor(0,0,0)
hdrPr=table.rows[0]._tr.get_or_add_trPr()
repeat=OxmlElement('w:tblHeader');repeat.set(qn('w:val'),'true');hdrPr.append(repeat)
for c in table.rows[0].cells:
 for p in c.paragraphs:
  for r in p.runs:r.bold=True

encabezado('Evidencias fotográficas')
for num,n in enumerate(['Vista general del sistema en Docker Desktop','Aplicación CampusSoporte con reportes','Creación y edición de una incidencia','Prueba de balanceo de carga','Grafana: panel de incidencias y tráfico','Portainer: servicios y volúmenes','Prueba de persistencia y falla de web2'],1):
 para(f'Evidencia {num}. ',n)
 blank('Insertar captura real aquí')
encabezado('Conclusión personal')
doc.add_paragraph('Con este proyecto entendí mejor cómo se relacionan los contenedores dentro de una misma aplicación. Al principio veía Docker como una herramienta para ejecutar programas por separado, pero al configurar Nginx, MariaDB y el monitoreo pude observar cómo cada servicio cumple una función. Me parece importante la persistencia porque evita que los reportes desaparezcan cuando se reinicia la infraestructura. Lo que más necesito practicar es la interpretación de los registros de Grafana y la solución de errores, ya que no basta con encender los contenedores: también hay que comprobar que realmente funcionan.')
doc.add_paragraph('Nota: ajustar esta conclusión según lo que realmente suceda durante la ejecución.')
doc.save(out)
print(out)
