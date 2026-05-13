import numpy as np, json, io
from PIL import Image, UnidentifiedImageError
from loguru import logger
from core.config import get_settings

settings = get_settings()

RISK_MAP = {
    "melanoma":               "high",
    "basal_cell_carcinoma":   "high",
    "squamous_cell_carcinoma":"high",
    "nevus":                  "low",
    "actinic_keratosis":      "medium",
    "seborrheic_keratosis":   "low",
    "dermatofibroma":         "low",
}
DESCRIPTIONS = {
    "melanoma":               "Lesão pigmentada com características suspeitas de malignidade.",
    "basal_cell_carcinoma":   "Possível carcinoma basocelular. Avaliação médica urgente necessária.",
    "squamous_cell_carcinoma":"Possível carcinoma espinocelular. Procure um dermatologista.",
    "nevus":                  "Nevo melanocítico benigno. Sem características suspeitas no momento.",
    "actinic_keratosis":      "Queratose actínica identificada. Acompanhamento dermatológico recomendado.",
    "seborrheic_keratosis":   "Queratose seborreica benigna. Acompanhamento periódico recomendado.",
    "dermatofibroma":         "Dermatofibroma identificado. Lesão benigna comum.",
}
RECOMMENDATIONS = {
    "high":   "⚠️ Procure atendimento dermatológico com urgência. Não adie esta consulta.",
    "medium": "Consulte um dermatologista nos próximos dias para avaliação.",
    "low":    "Acompanhe periodicamente. Consulte um dermatologista na próxima visita de rotina.",
}

class NevoPredictor:
    def __init__(self):
        self.model = None
        self.index_to_class = {}
        self._load()

    def _load(self):
        try:
            import tensorflow as tf
            self.model = tf.keras.models.load_model(settings.model_path)
            with open(settings.class_indices_path) as f:
                indices = json.load(f)
            self.index_to_class = {v: k for k, v in indices.items()}
            logger.info(f"✅ Modelo carregado: {settings.model_path}")
        except Exception as e:
            logger.warning(f"⚠️ Modelo não encontrado. Usando mock. Erro: {e}")

    def predict(self, image_bytes: bytes) -> dict:
        if not image_bytes:
            raise ValueError("Imagem vazia.")
        if self.model is None:
            return self._mock()
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
        except UnidentifiedImageError:
            raise ValueError("Arquivo de imagem inválido ou corrompido.")
        arr  = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)
        pred = self.model.predict(arr, verbose=0)[0]
        idx  = int(np.argmax(pred))
        conf = float(np.max(pred)) * 100
        cond = self.index_to_class.get(idx, "unknown")
        if conf < 50:
            return {"condition":"Inconclusivo","risk_level":"medium","confidence":round(conf,2),
                    "description":"Análise inconclusiva. Tente com uma foto com melhor iluminação.",
                    "recommendation":"Tire uma nova foto ou consulte um dermatologista presencialmente."}
        risk = RISK_MAP.get(cond, "medium")
        return {"condition": cond.replace("_"," ").title(), "risk_level": risk,
                "confidence": round(conf, 2), "description": DESCRIPTIONS.get(cond,""),
                "recommendation": RECOMMENDATIONS.get(risk,"")}

    def _mock(self):
        return {"condition":"Nevus","risk_level":"low","confidence":87.5,
                "description": DESCRIPTIONS["nevus"],
                "recommendation": RECOMMENDATIONS["low"]}

predictor = NevoPredictor()