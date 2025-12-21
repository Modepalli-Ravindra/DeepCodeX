from transformers import RobertaTokenizer, RobertaModel
import torch

# Load CodeBERT once
tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
model = RobertaModel.from_pretrained("microsoft/codebert-base")
model.eval()


def get_semantic_confidence(code: str) -> float:
    """
    Returns a semantic confidence score (0.0 - 1.0)
    based on embedding stability.
    This is NOT used for complexity calculations.
    """

    if not code.strip():
        return 0.0

    inputs = tokenizer(
        code,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    with torch.no_grad():
        outputs = model(**inputs)

    # Mean pooled embedding
    embedding = outputs.last_hidden_state.mean(dim=1)

    # Variance as semantic stability proxy
    variance = torch.var(embedding).item()

    # Normalize to 0–1 range (lower variance = higher confidence)
    confidence = 1 / (1 + variance)

    return round(confidence, 2)
