import os

import sys

from contextlib import asynccontextmanager

from typing import List, Literal, Optional



from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field, field_validator



_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_SRC = os.path.join(_ROOT, "src")

if _SRC not in sys.path:

    sys.path.insert(0, _SRC)



from evaluation.explain import explain_text, supports_lime  # noqa: E402

from models.predictor import ModelNotFoundError  # noqa: E402

from models.registry import load_predictor  # noqa: E402

from api.security import verify_api_key  # noqa: E402



ModelKind = Literal["tfidf", "bert"]

MAX_BATCH = 2000

MAX_TEXT_LEN = 5000

MAX_UPLOAD_BYTES = 5 * 1024 * 1024



_predictors: dict[str, object] = {}





def _get_predictor(model: ModelKind = "tfidf"):

    if model not in _predictors:

        try:

            _predictors[model] = load_predictor(model, root_dir=_ROOT)

        except Exception as exc:

            raise HTTPException(status_code=503, detail=str(exc)) from exc

    return _predictors[model]





@asynccontextmanager

async def lifespan(_: FastAPI):

    _get_predictor("tfidf")

    yield

    _predictors.clear()





app = FastAPI(

    title="Multilingual Sentiment API",

    description="Analyze comments with TF-IDF (fast) or BERT (accurate)",

    version="2.1.0",

    lifespan=lifespan,

)



app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)





class AnalyzeRequest(BaseModel):

    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LEN)

    language: Optional[str] = Field(default=None, pattern="^(en|ar_fusha|ar_shami)$")

    model: ModelKind = "tfidf"

    explain: bool = False





class BatchRequest(BaseModel):

    texts: List[str] = Field(..., min_length=1, max_length=MAX_BATCH)

    languages: Optional[List[Optional[str]]] = None

    auto_language: bool = True

    model: ModelKind = "tfidf"



    @field_validator("texts")

    @classmethod

    def validate_text_lengths(cls, texts: List[str]) -> List[str]:

        for index, text in enumerate(texts):

            if len(text) > MAX_TEXT_LEN:

                raise ValueError(f"Text at index {index} exceeds {MAX_TEXT_LEN} characters")

        return texts





@app.get("/")

def root():

    return {

        "service": "Multilingual Sentiment Analysis",

        "version": "2.1.0",

        "models": ["tfidf", "bert"],

        "endpoints": ["/api/v1/analyze", "/api/v1/batch", "/api/v1/health"],

    }





@app.get("/api/v1/health")

def health():

    tfidf_ok = os.path.exists(os.path.join(_ROOT, "models", "sentiment_model.pkl"))

    return {

        "status": "ok" if tfidf_ok else "model_missing",

        "tfidf_loaded": "tfidf" in _predictors,

        "bert_loaded": "bert" in _predictors,

    }





@app.post("/api/v1/analyze", dependencies=[Depends(verify_api_key)])

def analyze_one(request: AnalyzeRequest):

    predictor = _get_predictor(request.model)

    try:

        result = predictor.predict_with_confidence(request.text, language=request.language)

        if request.explain:

            if request.model != "tfidf" or not supports_lime(predictor):

                result["explanation"] = {

                    "explanation_available": False,

                    "message": "LIME is supported for TF-IDF model only.",

                }

            else:

                result["explanation"] = explain_text(

                    predictor, request.text, language=result["language"]

                )

        return result

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except ModelNotFoundError as exc:

        raise HTTPException(status_code=503, detail=str(exc)) from exc





@app.post("/api/v1/batch", dependencies=[Depends(verify_api_key)])

def analyze_batch(request: BatchRequest):

    predictor = _get_predictor(request.model)

    try:

        results = predictor.predict_batch(

            request.texts,

            languages=request.languages,

            auto_language=request.auto_language,

        )

        summary = {}

        for item in results:

            if item.get("error"):

                continue

            key = item["sentiment"]

            summary[key] = summary.get(key, 0) + 1



        return {"count": len(results), "summary": summary, "results": results, "model": request.model}

    except ModelNotFoundError as exc:

        raise HTTPException(status_code=503, detail=str(exc)) from exc





@app.post("/api/v1/batch/upload")

async def analyze_batch_upload(file: UploadFile = File(...), model: ModelKind = "tfidf"):

    import io



    import pandas as pd



    if not file.filename or not file.filename.lower().endswith(".csv"):

        raise HTTPException(status_code=400, detail="Upload a CSV file with a text column")



    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:

        raise HTTPException(status_code=400, detail="CSV file too large (max 5 MB)")



    df = pd.read_csv(io.BytesIO(content))

    if "text" not in df.columns:

        raise HTTPException(status_code=400, detail="CSV must contain a text column")



    texts = [str(v) for v in df["text"].tolist()]

    languages = None

    if "language" in df.columns:

        languages = [str(v) if pd.notna(v) else None for v in df["language"].tolist()]



    return analyze_batch(

        BatchRequest(texts=texts, languages=languages, auto_language=True, model=model)

    )


