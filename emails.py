import streamlit as st
import pandas as pd

st.set_page_config(page_title="Generador Emails", layout="wide")
st.title("📧 Generador de Emails de Facturación")

# Sidebar para configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    company_name = st.text_input("Nombre de la empresa:", value="EMPRESA", help="Se usa en el subject del email")
    
    st.subheader("📋 Opciones de contenido")
    include_ids = st.checkbox("Incluir IDs en los emails", value=True, help="Mostrar los Internal IDs en el detalle de cada proyecto")
    
    st.markdown("---")
    st.info("💡 Configura los parámetros básicos para personalizar los emails")

PROJECT_NAMES = {
    'MER286403207-ADNBRA25': 'ADN Brasil',
    'MER286403208-MER28640': 'ADN Argentina', 
    'MER286403209-ADNCOL25': 'ADN Colombia',
    'MER286403210-ADNMEX25': 'ADN México',
    'MER286403211-ADNURU25': 'ADN Uruguay',
    'MER286403258-CATALAR2': 'Leadership Workshops Argentina',
    'MER286403267-ADNCHI25': 'ADN Chile',
    'MER286403269-CATALUR': 'Leadership Workshops Uruguay',
    'MER286403270-CATALMX': 'Leadership Workshops México',
    'MER286403271-CATALCO': 'Leadership Workshops Colombia',
    'MER286403272-CATALCH': 'Leadership Workshops Chile',
    'MER286403273-CATALBR': 'Leadership Workshops Brasil'
}

def get_month_name(month_num):
    months = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
             7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
    return months.get(month_num, "Mayo")

def get_first_name(full_name):
    try:
        if ", " in str(full_name):
            return str(full_name).split(", ")[1].split()[0]
        return str(full_name)
    except:
        return str(full_name)

def generate_email(consultant_name, projects_data, month, company_name, include_ids):
    first_name = get_first_name(consultant_name)
    is_english = consultant_name == "De Castro Abreu, Silvia"
    
    if is_english:
        month_en = {"Abril": "april", "Mayo": "may", "Junio": "june"}.get(month, month.lower())
        subject = f"{company_name} - Fees {month_en} 2025 {first_name}"
        email = f"{subject}\n\nHi {first_name}, how are you?\n\nI hope you're doing well. Here are the details for {month_en} 2025 invoicing:\n\n"
        
        total = 0
        currency = ""
        
        for project_code, data in projects_data.items():
            project_name = PROJECT_NAMES.get(project_code, f"({project_code})")
            currency = data['currency']
            amount = data['total_cost']
            ids = ', '.join(data['internal_ids'])
            
            email += f"{project_name.upper()}\n"
            email += f"Project: {project_code}\n"
            
            # Mostrar actividades con rates
            for activity_data in data['activities'].values():
                email += f"- {activity_data['activity']}: {activity_data['hours']} hours @ {activity_data['currency']} {activity_data['rate']}/hour\n"
            
            # Incluir IDs solo si está habilitado
            if include_ids:
                email += f"- IDs: {ids}\n"
            
            email += f"- Subtotal: {currency} {amount:,.2f}\n\n"
            total += amount
        
        email += f"TOTAL TO INVOICE: {currency} {total:,.2f}\n\n"
        email += "Please remember:\n- Upload your invoice to AFN Support form: https://form.jotform.com/243515805505656\n- Include the project codes in your invoice\n\nBest regards!"
        
    else:
        subject = f"{company_name} - Fees {month.lower()} 2025 {first_name}"
        email = f"{subject}\n\nHola {first_name}, ¿cómo estás?\n\nTe envío el detalle para la facturación de {month.lower()} 2025:\n\n"
        
        total = 0
        currency = ""
        
        for project_code, data in projects_data.items():
            project_name = PROJECT_NAMES.get(project_code, f"({project_code})")
            currency = data['currency']
            amount = data['total_cost']
            ids = ', '.join(data['internal_ids'])
            
            email += f"{project_name.upper()}\n"
            email += f"Proyecto: {project_code}\n"
            
            # Mostrar actividades con rates
            for activity_data in data['activities'].values():
                email += f"- {activity_data['activity']}: {activity_data['hours']} horas @ {activity_data['currency']} {activity_data['rate']}/hora\n"
            
            # Incluir IDs solo si está habilitado
            if include_ids:
                email += f"- IDs: {ids}\n"
            
            email += f"- Subtotal: {currency} {amount:,.2f}\n\n"
            total += amount
        
        email += f"TOTAL A FACTURAR: {currency} {total:,.2f}\n\n"
        email += "Por favor recuerda:\n- Subir tu factura al formulario de AFN Support: https://form.jotform.com/243515805505656\n- Incluir los códigos de proyecto en tu factura\n\nSaludos!"
    
    return email

uploaded_file = st.file_uploader("Sube tu CSV", type=['csv'])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"✅ Archivo cargado: {len(df)} registros")
        
        # Detectar mes
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        month_num = df['Date'].dt.month.mode()[0] if not df['Date'].isna().all() else 5
        month = get_month_name(month_num)
        
        # Filtrar AFNM
        afnm_data = df[df['Employee Status'] == 'AFNM']
        st.info(f"📊 Encontrados: {len(afnm_data)} registros AFNM para {month}")
        
        if len(afnm_data) > 0:
            # Limpiar datos
            afnm_data = afnm_data.copy()
            afnm_data['Prj Code'] = afnm_data['Prj Code'].astype(str).str.strip()
            
            # Agrupar
            consultants = {}
            
            for _, row in afnm_data.iterrows():
                consultant = str(row['Consultant']).strip()
                project = str(row['Prj Code']).strip()
                internal_id = str(row['Internal ID'])
                activity = str(row['Activity']).split(' : ')[-1] if pd.notna(row['Activity']) else 'Activity'
                rate = float(row['Cost (Consultant Curr)']) if pd.notna(row['Cost (Consultant Curr)']) else 0
                hours = float(row['Total Hours']) if pd.notna(row['Total Hours']) else 0
                cost = float(row['Total Cost (Orig Currency)']) if pd.notna(row['Total Cost (Orig Currency)']) else 0
                currency = str(row['Consultant Currency']).strip()
                
                if consultant not in consultants:
                    consultants[consultant] = {}
                
                if project not in consultants[consultant]:
                    consultants[consultant][project] = {
                        'activities': {},
                        'internal_ids': [],
                        'total_cost': 0,
                        'currency': currency
                    }
                
                # Agrupar por actividad y rate
                activity_key = f"{activity}_{rate}"
                if activity_key not in consultants[consultant][project]['activities']:
                    consultants[consultant][project]['activities'][activity_key] = {
                        'activity': activity,
                        'rate': rate,
                        'hours': 0,
                        'currency': currency
                    }
                
                consultants[consultant][project]['activities'][activity_key]['hours'] += hours
                consultants[consultant][project]['internal_ids'].append(internal_id)
                consultants[consultant][project]['total_cost'] += cost
            
            # Generar emails
            emails = []
            for consultant_name, projects in consultants.items():
                email = generate_email(consultant_name, projects, month, company_name, include_ids)
                emails.append((consultant_name, email))
            
            st.success(f"🎉 Generados {len(emails)} emails para {month}")
            
            # Mostrar emails
            for i, (name, email) in enumerate(emails, 1):
                first_name = get_first_name(name)
                
                # Checkbox para marcar como enviado (fuera del expander)
                sent_checkbox = st.checkbox(f"✅ Email enviado a {first_name}", key=f"sent_{i}")
                
                # Determinar el ícono según el estado
                status_icon = "✉️" if sent_checkbox else "📧"
                status_text = " (ENVIADO)" if sent_checkbox else ""
                
                with st.expander(f"{status_icon} Email {i} - {first_name}{status_text}", expanded=not sent_checkbox):
                    
                    if sent_checkbox:
                        st.success(f"✉️ Marcado como enviado a {first_name}")
                    
                    st.info("💡 Selecciona todo el texto de abajo y cópialo con Ctrl+C / Cmd+C")
                    st.text_area("Email listo para copiar:", email, height=350, key=f"email_{i}")
                    
                    st.download_button(
                        f"⬇️ Descargar como archivo .txt",
                        email,
                        f"email_{first_name}_{month}.txt",
                        key=f"download_{i}",
                        use_container_width=True
                    )
            
            # Descargar todos
            all_emails = "\n\n" + "="*60 + "\n\n".join([email for _, email in emails])
            st.download_button(
                "⬇️ Descargar TODOS los Emails",
                all_emails,
                f"emails_facturacion_{month.lower()}.txt"
            )
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.write("Detalles del error:", e)