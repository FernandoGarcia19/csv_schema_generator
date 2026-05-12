JSON_SCHEMA_PROMPT = """
You are analyzing a table extracted from a report (financial, statistical, operational, etc.).
Your task is to infer the categorical dimensional structure required to convert the table into a flattened long dataset.
The final dataset will always contain:
fecha
valor
Your job is ONLY to detect the categorical dimensions that define each numeric value.

OBJECTIVE
Identify the categorical structure of the table and represent it as generic hierarchy levels:
nv1, nv2, nv3 ... nvN
These levels come from two sources:
1 Row dimensions (hierarchical)
2 Column dimensions (usually a single level)

STEP 1 — Identify Numeric Cells
Locate the cells containing numeric values.
These represent the FACT ("valor").
Numeric cells must NOT appear in the dimension member lists.

STEP 2 — Identify Row Dimension (Hierarchical)
The left side of the table usually contains the main categorical hierarchy.
This dimension often represents things like:
accounts
product categories
economic sectors
geographic breakdowns
statistical classifications
This row dimension may contain multiple hierarchical levels.

Rules:
• Use indentation, alignment, and grouping to detect hierarchy.
• Parent rows represent higher nv levels.
• Child rows represent deeper nv levels.

Constraint: A categorical level (nvX) must represent a variable. 
If a name or entity applies to every single numeric value in the table (e.g., the name of the company at the top of a report), 
it is Metadata, not a Dimension. Do not include constant Metadata as an nv level.

STEP 3 — Identify Column Dimension
Column headers often represent entities measured across the same categories, such as:
institutions
companies
regions
years
scenarios

STEP 4 — Determine Hierarchy Depth
Combine the row hierarchy levels and the column dimension to form the final structure. Row dimensions come first followed by the column dimensions. 

STEP 5 — Extract Members
For each level (nvX), return the list of possible members found in the table.
Rules:
• Members must be unique
• Maximum 10 elements per level
• Ignore empty cells
• Ignore numeric values
• Ignore formatting artifacts

OUTPUT FORMAT
Return ONLY a JSON object.
Keys must be sequential:
nv1
nv2
nv3
...
nvN
"""

CSV_GENERATOR_PROMPT = """
Task:  Map the provided JSON hierarchical schema to the table image to produce a flattened, sparse CSV SAMPLE.
Structural Rules:
Mandatory Columns: The output MUST end with the columns fecha and valor.
Global Attributes: Extract the date from the table header/title and populate the fecha column if there is no date inside the table data.
Fact Extraction: The valor column must contain the numerical data. Represent empty/dash cells as - and ensure negative numbers (often in red or parentheses) retain their negative sign.
Output Requirements:
Generate a CSV code block.
Header format: nv1,nv2,nv3,...,nvN,fecha,valor
Quote any field that contains commas, line breaks, or double quotes so the CSV remains parseable.
For the Fecha Valor, in the case that date is specified in rows or columns (i. e. composed columns with "2023" and "2024" deglossed into Enero, Febrero, Marzo, etc.) but the exact day is missing, fill the date as the last day of the corresonding month.
For example: If a compossed column has "2023" and "enero", the fecha should be "2023-01-31".
Ensure the hierarchy follows the visual "indentation" or "bolding" cues from the image and the structure identified in the JSON. ONLY return the CSV sample.
Return up to only 30 rows of sample data.
Make sure to maintain the numeric value in "valor". Do not truncate it. 
In the extremely rare case that the image contains no numeric attribute for "Valor", populate the "valor" column with a placeholder value of 1.
"""