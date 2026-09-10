from google import genai
from google.genai import types
import base64
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field
from datetime import date

#=====INPUT=====
PDF_PATH = './data/demo/GI log/32478 BH1 Logs.pdf'

system_prompt = """
You are an expert geotechnical data extraction AI. 
Extract the requested fields from the provided Geotechnical Investigation (GI) 
log PDF and format the output according to the provided Pydantic JSON schema.
"""
prompt = """
Extract this GI log pdf file information.
# Instructions:

## Extraction for Header Metadata
Extract the GI name, easting coordinates, 
northing coordinates, date of GI, contract number, and ground level (mPD).

## Extraction for Soil Layers (Array)
For every layer present, which is delimited by numbers 
and horizontal lines in "Reduced Level" and "Depth" column of the GI log, 
extract the top and bottom reduced levels (mPD), top and bottom depths (m), 
and the full text description on the right side of the legend and grade column.

### Segmentation
1. Depth Line Splits: Split layers at every horizontal line boundary or 
intermediate value in the "Depth" / "Reduced Level" columns.
2. Inline Range Splits: Create a new layer record when an inline depth prefix 
(e.g., "9.10-10.00m:") appears in the description box.
3. Sub-layer & Page Inheritance: For incremental sub-layers or 
multi-page continuations (e.g., "As sheet 1 of 3"), 
inherit `material_origin`, `grain_size`, and `grade` from the preceding 
layer/page, then append the sub-layer text to the primary description.

### Classification Parsing
Analyze the full description text for each layer. 
Extract the "Material Origin" (must be the FIRST fully CAPITALIZED word 
in the description, such as ALLUVIUM, COLLVUIUM, GRANITE) and the 
"Grain Size" (must be the fully CAPITALIZED word inside the parenthesis in 
the description, such as GRAVEL, SAND, SILT, CLAY). 
Skip COBBLE for the grain size output. Instead, set cobble existence to True 
for that layer.
If "Material Origin" and "Grain Size" is missing in that layer, use the 
same "Material Origin" and "Grain Size" of the previous layer.
Output strictly in JSON.
If the grade of the soil layer is missing, use the same "Grade" 
of the previous layer.
If the grade of the soil layer is in [III, II, I], 
return the "Grain Size" to ROCK. 
If the grade of the soil layer is in [V, IV], keep the "Grain Size".

#Example for extraction of Grain Size and Material Origin from description
## Example 1
### Description
Extremely week, yellowish brown (10YR5/8), 
completely decomposed meta fine ash TUFF.
(Very stiff, sandy SILT)
### Output for example 1
Material Origin = TUFF
Grain Size = SILT
Cobble existence = False

## Example 2
### Description
Very weak, yellowish brown (10YR5/8), completely to highly decomposed 
meta fine ash TUFF. (Very silty fine to medium SAND with 
occasional cobble of weak tuff)
### Output for example 2
Material Origin = TUFF
Grain Size = SAND
Cobble existence = True
"""
#=====End of INPUT=====

load_dotenv()
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

#=====Define json schema=====
class Soil(BaseModel):
    reduced_level_top: float = Field(description='Top level of the ' \
    'soil layer in mPD')
    reduced_level_bot: float = Field(description='Bottom level of the ' \
        'soil layer in mPD')
    depth_top: float = Field(description='Depth at the top of soil layer ' \
    'from ground level in mPD')
    depth_bot: float = Field(description='Depth at the bottom of soil layer ' \
    'from ground level in mPD')
    description:str = Field(description='Full soil description of the soil ' \
    'layer in the "Description" box of the GI log')
    grade: str = Field(description='Rock grade of the soil layer ' \
        'in the "Grade" box of the GI log.' \
        'Inherit the immediate extracted segment above if missing')
    material_origin: str = Field(description='Material origin classification' \
    ', must be the FIRST fully CAPITALIZED word in the description, ' \
    'such as ALLUVIUM, COLLVUIUM, GRANITE. ' \
    'Inherit the immediate extracted segment above if missing')
    grain_size: str = Field(description='Grain size classification, must be ' \
    'the fully CAPITALIZED word inside the parenthesis in the description' \
    'of the soil layer, such as GRAVEL, SAND, SILT, CLAY.' \
    'Inherit the immediate extracted segment above if missing.' \
    'Set to "ROCK" if grade is III, II, or I')
    cobble_exists: bool = Field(description='Existence of cobble in the ' \
    'soil layer. True if cobble exists.')

class Gi_stick(BaseModel):
    name: str = Field(description='Name or number of the GI stick')
    easting: float = Field(description='Easting coordinate, \
    based on HK1980 Grid System, of the GI stick', 
    gt=799000.00, lt=850000.00)
    northing: float = Field(description='Northing coordinate, \
    based on HK1980 Grid System, of the GI stick', 
    gt=799000.00, lt=872000.00)
    gi_date: date = Field(description='Date of GI stick in the log')
    contract: str = Field(description='Corresponding contract of the GI log')
    ground_level: float = Field(description='Ground level of \
    the GI the log in mPD')
    soil: list[Soil] = Field(description='Soil layer of the GI log, from \
    highest elevation in mPD to lowest elevation in mPD')
#=====End of define json schema=====

#=====LLM interaction=====
with open(PDF_PATH, 'rb') as f:
    pdf_bytes = f.read()
pdf_data = base64.b64encode(pdf_bytes).decode("utf-8")

interaction = client.interactions.create(
    model='gemini-3.5-flash',
    system_instruction=system_prompt,
    input=[
        {
            'type': 'document',
            'data': pdf_data,
            'mime_type': 'application/pdf'
        },
        {
            'type': 'text',
            'text': prompt
        },
    ],
    response_format={
        'type': 'text',
        'mime_type': 'application/json',
        'schema': Gi_stick.model_json_schema()
    },
    generation_config={
        "temperature": 0.01
    }
)
#=====End of LLM interaction=====

gi = Gi_stick.model_validate_json(interaction.output_text)

#=====Formatted output=====
print(f'{'Summary':=^50}')
print(f'Name: {gi.name}')
print(f'Coordinate: E{gi.easting}, N{gi.northing}')
print(f'Date: {gi.gi_date}')
print(f'Contract: {gi.contract}')
print(f'Ground level: {gi.ground_level}mPD')
print(f'{'Soil layer':-^50}')
for s in gi.soil:
    elevation_str = f'{s.reduced_level_top}mPD to {s.reduced_level_bot}mPD'
    depth_str = f'(Depth {s.depth_top}m to {s.depth_bot}m)'
    if s.grade:
        soil_str = f'{s.grain_size} {s.material_origin} (Grade {s.grade})'
    else:
        soil_str = f'{s.grain_size} {s.material_origin}'
    cobble_str = '(Cobble exists)'
    str_list = [elevation_str, depth_str, soil_str]
    if s.cobble_exists:
        str_list.append(cobble_str)
    output_str = ' '.join(str_list)
    print(output_str)
#=====End of formatted output=====