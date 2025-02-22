import os
from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import MolDraw2DSVG

def generate_svg_from_smiles(smiles, filename):
    """Generates an SVG from a SMILES string and saves it as a file."""
    mol = Chem.MolFromSmiles(smiles)
    if not mol:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    rdDepictor.Compute2DCoords(mol)
    drawer = MolDraw2DSVG(300, 300)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()

    # Fix rendering issues with background and strokes
    svg = svg.replace("fill:white", "fill:none")
    svg = svg.replace("fill:#FFFFFF", "fill:none")
    svg = svg.replace("stroke:#000000", "stroke-opacity:1")

    with open(filename, "w") as f:
        f.write(svg)
    
    return filename
