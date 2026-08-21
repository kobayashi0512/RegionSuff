# MMRDR: Multi-Modal Retinal images for in-depth DR analysis

## Dataset Structure

```bash
MMRDR/
├── MMRDR-CFP/            # Color Fundus Photography
│   ├── img/              # CFP images (JPEG format)
│   │   ├── tr000001.jpg  # Training case 1
│   │   ├── tr000002.jpg  # Training case 2
│   │   ├── ...
│   │   ├── ts000001.jpg  # Testing case 1
│   │   └── ... 
│   └── FP.csv            # Metadata & annotations
│
├── MMRDR-OCT/            # Optical Coherence Tomography
│   ├── img/              # OCT images (JPEG format)
│   │   ├── tr000001.jpg  # Training case 1
│   │   ├── ...
│   │   ├── ts000001.jpg  # Testing case 1
│   │   └── ... 
│   └── OCT.csv           # Metadata & annotations
│
└── MMRDR-UWF/            # Ultra-WideField Imaging
    ├── img/              # UWF images (JPEG format)
    │   ├── tr000001.jpg  # Training case 1
    │   ├── ...
    │   ├── ts000001.jpg  # Testing case 1
    │   └── ... 
    └── UWF.csv           # Metadata & annotations
```

## Annotation Specifications
### Shared Fields (All Modalities)
| Field     | Values          | Description                     |
|-----------|-----------------|---------------------------------|
| **`lr`**  | `0` = Left eye<br>`1` = Right eye | Laterality identifier           |

### Modality-Specific Annotations
**1. CFP & UWF Annotations** (`FP.csv`, `UWF.csv`)
| Field       | Values | Description                                  |
|-------------|--------|----------------------------------------------|
| **`grade`** | `0`: No DR<br>`1`: Mild NPDR<br>`2`: Moderate NPDR<br>`3`: Severe NPDR<br>`4`: PDR | Diabetic retinopathy severity grading |
| **`lesion`**| List of 7 binary values `[v₁,v₂,...,v₇]`<br>`0`=Absent, `1`=Present | **Lesion types in order:**<br>1. Microaneurysm<br>2. Hard exudate<br>3. Intraretinal hemorrhage<br>4. VB/IRMA (Venous beading/Intraretinal microvascular abnormalities)<br>5. Neovascularization<br>6. Vitreous hemorrhage<br>7. Retinal detachment |

**2. OCT Annotations** (`OCT.csv`)
| Field       | Values | Description                     |
|-------------|--------|---------------------------------|
| **`grade`** | `0`: No DME<br>`1`: NCI DME (Non-Center Involved DME)<br>`2`: CI DME (Center-Involved DME) | Diabetic Macular Edema grading |
