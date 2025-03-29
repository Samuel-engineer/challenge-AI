import streamlit as st
import datetime
import os
import sys
import importlib.util

# Ajouter les chemins vers les modules
sys.path.append("../data battle/app")

from api_utils import get_api_response

# ➕ Générer un ID de session unique pour l'utilisateur
def get_session_id():
    st.session_state.session_id = f"session_1_{st.session_state.id}"
    return st.session_state.session_id

# 🔁 Fonction qui interroge le chatbot après création du questionnaire
def send_questionnaire_request(user_data):
    session_id = get_session_id()

    # Génère un prompt structuré pour le chatbot
    prompt = (
        f"Génère un questionnaire sur les thèmes suivants :\n"
        f"- Catégories : {', '.join(user_data['categories'])}\n"
        f"- Sous-catégories : {', '.join(user_data['subcategories'])}\n"
        f"- Types de questions : {', '.join(user_data['question_types'])}\n"
        f"Nombre de questions : {user_data['num_questions']}\n"
    )

    # Appel API RAG avec tous les paramètres nécessaires
    rag_response = get_api_response(prompt, session_id=session_id, model="mistral-large-latest")

    # Gestion des erreurs
    if rag_response and isinstance(rag_response, dict):
        chatbot_message = rag_response.get("answer", "⚠ Aucune réponse reçue.")
    else:
        chatbot_message = "❌ Erreur : l'API n'a pas répondu correctement."

    return {"chatbot_response": chatbot_message}

# 🔁 Placeholder pour future fonctionnalité
def retake_questionnaire():
    st.subheader("Repasser un questionnaire")
    st.text("Fonctionnalité en cours de développement.")

# 🎯 Application principale Streamlit
def main():
    st.markdown("""
        <style>
        .main-title { font-size: 32px; color: #3F3D56; font-weight: bold; }
        .info-text { font-size: 16px; color: #6B7280; }
        .stButton>button {
            background-color: #1E3A8A; color: white;
            font-size: 16px; font-weight: 600;
            padding: 10px; border-radius: 5px;
        }
        .stButton>button:hover { background-color: #4C51BF; }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: st.image("logo1.jpeg", width=100)
    with col2: st.image("logo.jpeg", width=100)
    with col3: st.image("LOGO_EFREI.jpeg", width=150)

    st.markdown('<p class="main-title">📄 Générateur de Questionnaire - Propriété Intellectuelle</p>', unsafe_allow_html=True)

    nav = st.radio("Navigation", ("Créer un questionnaire", "Historique des questionnaires", "Chatbot"), horizontal=True)

    if nav == "Créer un questionnaire":
        st.markdown('<p class="info-text">Sélectionnez les catégories, sous-catégories et types de questions.</p>', unsafe_allow_html=True)

        categories = {
            "1. Filing requirements and formalities": [
                "1.1 Minimum requirements for a filing date", "1.2 Filing methods and locations", "1.3 Formality examination"
            ],
            "2. Priority claims and right of priority": [
                "2.1 Substantive requirements for priority", "2.2 Time limits and restoration", "2.3 Multiple priorities and partial priority"
            ],
            "3. Divisional applications": [
                "3.1 Filing requirements", "3.2 Subject-matter and scope", "3.3 Fees for divisionals"
            ],
            "4. Fees, payment methods, and time limits": [
                "4.1 Types and calculation of fees", "4.2 Payment mechanisms", "4.3 Fee deadlines and late payment consequences"
            ],
            "5. Languages and translations": [
                "5.1 Language of filing and procedural language", "5.2 Translation requirements", "5.3 Effects on rights"
            ],
            "6. Procedural remedies and legal effect": [
                "6.1 Further processing", "6.2 Re-establishment of rights", "6.3 Loss of rights and remedies"
            ],
            "7. PCT procedure and entry into the European phase": [
                "7.1 International filing", "7.2 Preliminary examination", "7.3 European phase entry"
            ],
            "8. Examination, amendments, and grant": [
                "8.1 Examination procedure", "8.2 Claim amendments", "8.3 Grant stage and publication"
            ],
            "9. Opposition and appeals": [
                "9.1 Grounds for opposition", "9.2 Procedure and admissibility", "9.3 Appeal proceedings"
            ],
            "10. Substantive patent law": [
                "10.1 Novelty analysis", "10.2 Inventive step", "10.3 Special claim types"
            ],
            "11. Entitlement and transfers": [
                "11.1 Entitlement disputes", "11.2 Transfers", "11.3 Consequences"
            ],
            "12. Biotech and sequence listings": [
                "12.1 Sequence listing", "12.2 Subject-matter", "12.3 Exceptions"
            ],
            "13. Unity of invention": [
                "13.1 Unity in EP applications", "13.2 Unity in PCT", "13.3 Strategies"
            ]
        }

        selected_categories = st.multiselect("📌 Choisissez les catégories :", list(categories.keys()))
        selected_subcategories = [sub for cat in selected_categories for sub in st.multiselect(f"📂 Sous-catégories pour {cat} :", categories[cat])]
        question_types = st.multiselect("❓ Types de questions :", ["QCM", "Vrai_ou_faux", "Réponses ouvertes"])
        num_questions = st.number_input("🔢 Nombre de questions :", min_value=5, step=1, value=10)
        num_choices = st.slider("📊 Nombre de choix :", 2, 4, 2) if "QCM" in question_types else None

        if st.button("📌 Enregistrer et Générer"):
            user_data = {
                "categories": selected_categories,
                "subcategories": selected_subcategories,
                "question_types": question_types,
                "num_questions": num_questions,
                "num_choices": num_choices
            }

            result = send_questionnaire_request(user_data)
            if "chatbot_response" in result:
                st.success("✅ Questionnaire généré avec succès !")
                st.subheader("💬 Réponse du chatbot")
                st.write(result["chatbot_response"])
            else:
                st.error("❌ Erreur lors de la génération du questionnaire.")

    elif nav == "Historique des questionnaires":
        chat_path = os.path.normpath("../data battle/app/streamlit_app.py")
        if os.path.exists(chat_path):
            spec = importlib.util.spec_from_file_location("questionnaire", chat_path)
            mon_questionnaire = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mon_questionnaire)
        else:
            st.error("❌ Fichier d'historique introuvable !")

    elif nav == "Chatbot":
        chat_path = os.path.normpath("../data battle/app/streamlit_app.py")
        if os.path.exists(chat_path):
            spec = importlib.util.spec_from_file_location("chatbot", chat_path)
            chatbot_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(chatbot_module)
        else:
            st.error("❌ Fichier du chatbot introuvable !")


if __name__ == "__main__":
    main()
   