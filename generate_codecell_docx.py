"""
Generate a .docx explaining every code cell (line-by-line) from the detection_intention notebook.
Only code cells are processed. Explanations are simple and include reasoning for choices when detectable.
"""
import json
import re
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

NOTEBOOK_PATH = 'notebooks/detection_intention.ipynb'
OUTPUT_PATH = 'Detection_Intention_Code_Explanation.docx'

# Simple heuristics mapping (regex -> (short explanation, reason))
PATTERNS = [
    (r"^import\s+torch", ("Import the PyTorch library.", "Used for tensor operations and to check GPU availability and for model training.")),
    (r"^from\s+transformers\s+import", ("Import Transformers components.", "We use Hugging Face Transformers for tokenization, modelling and training.")),
    (r"^!pip install", ("Install Python packages in the Colab environment.", "Ensures required dependencies (transformers, datasets, etc.) are available in the notebook runtime.")),
    (r"drive\.mount\(", ("Mount Google Drive.", "Allows reading and writing datasets/models on Google Drive in Colab.")),
    (r"os\.environ\[.*WANDB_DISABLED", ("Disable Weights & Biases logging.", "Avoids external experiment tracking to keep runs lightweight and private.")),
    (r"os\.makedirs\(|os\.path\.join", ("Create / join filesystem paths.", "Set up working directories consistently (works on Colab and local).")),
    (r"pd\.read_csv\(", ("Load a CSV file into a pandas DataFrame.", "Used to read train/test datasets; pandas is convenient for analysis and preprocessing.")),
    (r"LabelEncoder\(|label_encoder", ("Encode string labels to integer IDs.", "Required by ML frameworks which expect numeric labels for classification.")),
    (r"AutoTokenizer\.from_pretrained\(|tokenizer =", ("Load a pretrained tokenizer (CamemBERT).", "Tokenization converts raw text to token ids compatible with the model; CamemBERT is a French pretrained model.")),
    (r"def\s+tokenize_function", ("Define a tokenization function for the dataset.", "Centralizes tokenization parameters like max length and truncation for consistent preprocessing.")),
    (r"Dataset\.from_pandas\(|intent_train_dataset", ("Create a HuggingFace Dataset from a pandas DataFrame.", "Datasets work well with the Trainer API and can be tokenized with map().")),
    (r"AutoModelForSequenceClassification\.from_pretrained", ("Load a pretrained sequence classification model (CamemBERT).", "We fine-tune a pretrained model to save training time and improve performance on French text.")),
    (r"compute_class_weight\(|class_weights", ("Compute class weights for imbalanced classes.", "Gives more importance to minority classes during loss computation to reduce bias.")),
    (r"class\s+WeightedTrainer\(|CrossEntropyLoss\(|weight=weight_tensor", ("Custom Trainer using a weighted loss.", "Applies class weights to the loss so the model treats minority classes fairly.")),
    (r"TrainingArguments\(|num_train_epochs|per_device_train_batch_size|learning_rate", ("Define training hyperparameters.", "Controls epochs, batch size, learning rate and other aspects of training stability and performance.")),
    (r"intent_trainer\.train\(|ner_trainer\.train\(|trainer\.train\(\)", ("Start model fine-tuning.", "Runs gradient updates on training data to adapt the pretrained model to the target task.")),
    (r"intent_trainer\.evaluate\(|ner_trainer\.evaluate\(|predict\(|classification_report", ("Evaluate the model on the test set and compute metrics.", "Gives objective performance measures like accuracy and F1 to assess model quality.")),
    (r"langdetect|detect\(|from\s+langdetect", ("Detect text language.", "Used in post-processing to separate non-French queries (NOT_FRENCH) from French ones.")),
    (r"def\s+post_process_prediction", ("Define post-processing heuristics for intent predictions.", "Rules correct systematic errors (language detection, keywords) that the classifier alone may mishandle.")),
    (r"json\.loads\(|parse_entities_field", ("Parse JSON-encoded entity annotations.", "Validates entity offsets for NER training and avoids corrupted annotations.")),
    (r"AutoModelForTokenClassification\.from_pretrained|DataCollatorForTokenClassification", ("Load token-classification model and data collator.", "Used for NER to tag tokens with BIO labels (Departure/Destination).")),
    (r"return_offsets_mapping=True|offset_mapping", ("Use offset mapping during tokenization.", "Necessary to align token indices with character offsets for BIO labeling.")),
    (r"pipeline\(|from\s+transformers\s+import\s+pipeline", ("Create Hugging Face inference pipelines.", "Simplifies running the trained models for intent classification and NER during inference.")),
]

# Fallback explanation when none of the patterns match
FALLBACK = ("Execute a Python statement.", "Line performs a standard Python operation; explanation omitted because it was simple or repetitive.")


def explain_line(line):
    stripped = line.strip()
    if not stripped:
        return None  # skip empty lines

    # check common patterns
    for pattern, (explanation, reason) in PATTERNS:
        if re.search(pattern, stripped):
            return explanation, reason

    # heuristics for assignments, function defs, control flow
    if stripped.startswith("#"):
        return ("Comment: " + stripped.lstrip('#').strip(), "Comment describing code intent.")
    if stripped.startswith("def "):
        return ("Define function.", "Creates a reusable function used later in the notebook.")
    if stripped.startswith("for ") or stripped.startswith("if ") or stripped.startswith("while "):
        return ("Control flow statement.", "Alters execution path (loop/conditional).")
    if "=" in stripped and not stripped.startswith("==") and not stripped.startswith("+="):
        return ("Assign a value to a variable.", "Stores computation results or config values for later use.")

    # fallback
    return FALLBACK


def create_doc(notebook_path, output_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    doc = Document()
    doc.styles['Normal'].font.name = 'Arial'
    title = doc.add_heading('Explication cellule-par-cellule (code seulement) - detection_intention', level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    intro = doc.add_paragraph()
    intro.add_run('Ce document explique, ligne par ligne, toutes les cellules de code du notebook "detection_intention.ipynb". ').bold = True
    intro.add_run('Seules les cellules de code sont couvertes; les cellules markdown sont ignorees.\n\n')
    intro.add_run('Pour chaque ligne :\n - Une explication simple de ce que fait la ligne\n - La raison du choix lorsque elle est detectee\n')

    code_cells = [c for c in nb.get('cells', []) if c.get('cell_type') == 'code']

    for idx, cell in enumerate(code_cells, start=1):
        doc.add_heading(f'Cellule de code {idx}', level=2)

        # show the original code block
        code_block = '\n'.join(cell.get('source', []))
        p = doc.add_paragraph()
        run = p.add_run('Code:\n')
        run.bold = True
        code_para = doc.add_paragraph(code_block)
        code_para.style = doc.styles['Normal']
        code_para.paragraph_format.left_indent = Inches(0.25)
        code_para.runs[0].font.name = 'Courier New'
        code_para.runs[0].font.size = Pt(9)

        doc.add_paragraph('\nExplications ligne par ligne :')

        lines = code_block.split('\n')
        for lineno, line in enumerate(lines, start=1):
            expl = explain_line(line)
            if expl is None:
                continue
            explanation, reason = expl
            # write line number and code
            line_para = doc.add_paragraph()
            line_para.add_run(f'{lineno:03d} | ').bold = True
            code_run = line_para.add_run(line.rstrip())
            code_run.font.name = 'Courier New'
            code_run.font.size = Pt(9)

            # explanation
            expl_para = doc.add_paragraph()
            expl_para.paragraph_format.left_indent = Inches(0.35)
            expl_para.add_run('Explication: ').bold = True
            expl_para.add_run(explanation)

            # reason
            reason_para = doc.add_paragraph()
            reason_para.paragraph_format.left_indent = Inches(0.35)
            reason_para.add_run('Raison / Choix: ').bold = True
            reason_para.add_run(reason)

        doc.add_page_break()

    doc.save(output_path)
    print(f'Generated: {output_path}')


if __name__ == '__main__':
    create_doc(NOTEBOOK_PATH, OUTPUT_PATH)
