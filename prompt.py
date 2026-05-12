JSON_SCHEMA_PROMPT_CATEGORY_1 = """
You are an expert data extraction agent. We are extracting flattened CSV schemas from report tables categorized as 'Simple Tables (No Indentation)'.

RULES FOR SIMPLE TABLES:

Scan the table from left to right.

Ignore any columns representing dates (e.g., 'fecha', 'periodo') or fact dimensions/values (e.g., 'valor', 'saldo', numerical amounts).

Assign each remaining categorical column a sequential level starting from nv1, nv2, nv3, etc.

Extract all the unique string values present in each identified column and return a strict JSON object mapping each level to its array of unique values.

Your output MUST be a JSON object with the following structure:
{
"nv1":[....], "nv2":[....], "nv3":[....], ... "nvN":[....]
}
Your output will be fed to another sprompt to generate the final CSV sample with nv1,nv2,...nvN, fecha,valor.
"""

JSON_SCHEMA_PROMPT_CATEGORY_2 = """
Identify Row Hierarchy: Scan the leftmost columns to detect hierarchical groupings in the rows. This hierarchy is typically indicated by visual indentation, numbering schemes (e.g., 1, 1.1, 1.1.1), font weighting (bolding), or merged vertical cells.

Assign Sequential Levels: Map the highest/broadest row category to nv1. Map the first nested sub-category to nv2, the next to nv3, and so on, continuing until you reach the deepest level of row indentation.

Process Remaining Columns: After fully mapping the nested rows, assign any remaining standalone categorical column headers to the subsequent nv levels.

Exclude Facts & Dates: Strictly ignore any cells or columns representing dates (e.g., 'fecha', 'periodo') or fact dimensions/values (e.g., 'valor', 'saldo', 'total', numerical amounts).

Output Format: Extract all the unique string values present in each identified hierarchical level. Return a strict JSON object mapping each sequential level (nv1, nv2, etc.)
Your output MUST be a JSON object with the following structure:
{
"nv1":[....], "nv2":[....], "nv3":[....], ... "nvN":[....]
}
Your output will be fed to another prompt to generate the final CSV sample with nv1,nv2,...nvN, fecha,valor.

"""

JSON_SCHEMA_PROMPT_CATEGORY_3 = """
You are an expert data extraction agent. We are extracting flattened CSV schemas from report tables categorized as 'Composed Columns'.

RULES FOR COMPOSED COLUMNS:

Identify Multi-Level Headers: Scan the top rows of the table to detect horizontal hierarchical groupings. Look for overarching primary headers that visually span across or group multiple sub-columns below them (e.g., a master header like 'DEPÓSITOS' sitting above sub-headers like 'MN' and 'ME').

Map the Leftmost Row Categories: First, identify the primary row categories in the leftmost column(s) (e.g., 'año', 'departamento') and assign them to the initial level(s), such as nv1.

Map the Horizontal Hierarchy (Top-Down): Next, assign the highest/broadest column header (the "super-header") to the next sequential level (e.g., nv2). Assign the nested sub-headers below it to subsequent levels (e.g., nv3, nv4, etc.), continuing downwards until you reach the final header row immediately above the numerical data grid.

Exclude Facts: Strictly ignore the numerical data points, values, or amounts located in the main body/grid of the table. Your goal is only to extract the categorical structure.

Output Format: Extract all the unique string values present in each identified hierarchical level. Return a strict JSON object mapping each sequential level (nv1, nv2, nv3, etc.) to its array of unique string values. Return ONLY the raw JSON object. Do not use markdown wrappers like ```json.
Your output MUST be a JSON object with the following structure:
{
"nv1":[....], "nv2":[....], "nv3":[....], ... "nvN":[....]
}
Your output will be fed to another prompt to generate the final CSV sample with nv1,nv2,...nvN, fecha,valor.
"""

JSON_SCHEMA_PROMPT_CATEGORY_4 = """
You are an expert data extraction agent. We are extracting flattened CSV schemas from report tables categorized as 'Mixed Tables (Composed Rows and Columns)'.

RULES FOR MIXED TABLES:

Identify Dual Hierarchies: Analyze the table to detect both vertical (row) groupings on the left and horizontal (column) groupings at the top.

Map the Row Hierarchy (Vertical): Scan the leftmost columns first. Identify overarching thematic blocks or parent rows (e.g., 'Disponibilidades', 'Inversiones') and assign them to nv1. Identify any indented or grouped sub-rows within those blocks and assign them to subsequent levels (e.g., nv2). Continue until the deepest row hierarchy is mapped.

Map the Column Hierarchy (Horizontal): Once the row levels are fully assigned, analyze the top header rows. Identify the highest-level overarching column headers (super-headers) and assign them to the next available sequential level (e.g., nv3). Map the nested sub-headers below them to the subsequent level (e.g., nv4), continuing top-down through the header rows.

Exclude Facts: Strictly ignore all numerical data points, values, or amounts located inside the main body/grid of the table. Your goal is only to extract the categorical structure from the headers and row stubs.

Output Format: Extract all the unique string values present in each identified hierarchical level. Return a strict JSON object mapping each sequential level (nv1, nv2, nv3, nv4, etc.) to its array of unique string values. Return ONLY the raw JSON object. Do not use markdown wrappers like ```json.
Your output MUST be a JSON object with the following structure:
{
"nv1":[....], "nv2":[....], "nv3":[....], ... "nvN":[....]
}
Your output will be fed to another prompt to generate the final CSV sample with nv1,nv2,...nvN, fecha,valor.
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
