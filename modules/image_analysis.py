"""
Image Analysis Module
----------------------
Evaluates the reliability of an uploaded claim image.

Checks performed:
    - Missing image
    - Blurry image (Laplacian variance)
    - Duplicate image (perceptual hash against a known-image store)
    - Low-resolution / low-quality evidence

Output:
    Image Reliability Score (0-100, higher = more reliable)
"""

import os
import hashlib
from typing import Dict, Optional

import cv2
import numpy as np
from PIL import Image


BLUR_THRESHOLD = 100.0          # Laplacian variance below this = blurry
MIN_RESOLUTION = (400, 400)     # (width, height) below this = low quality


def _compute_blur_score(gray_image: np.ndarray) -> float:
    """Higher variance = sharper image. Lower variance = blurrier image."""
    return cv2.Laplacian(gray_image, cv2.CV_64F).var()


def _compute_image_hash(image_path: str) -> str:
    """Simple perceptual-style hash used to flag likely duplicate uploads."""
    with Image.open(image_path) as img:
        img = img.convert("L").resize((16, 16))
        pixels = np.asarray(img).flatten()
        avg = pixels.mean()
        bits = "".join("1" if p > avg else "0" for p in pixels)
        return hashlib.md5(bits.encode()).hexdigest()


def analyze_image(image_path: Optional[str], known_hashes: Optional[set] = None) -> Dict:
    """
    Analyze a claim image and return a reliability report.

    Args:
        image_path: Path to the uploaded claim image.
        known_hashes: Set of perceptual hashes from previously submitted
                       images, used to flag duplicates.

    Returns:
        dict with keys: reliability_score, is_missing, is_blurry,
        is_duplicate, is_low_resolution, image_hash
    """
    known_hashes = known_hashes or set()

    if not image_path or not os.path.exists(image_path):
        return {
            "reliability_score": 0,
            "is_missing": True,
            "is_blurry": False,
            "is_duplicate": False,
            "is_low_resolution": False,
            "image_hash": None,
        }

    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        return {
            "reliability_score": 0,
            "is_missing": True,
            "is_blurry": False,
            "is_duplicate": False,
            "is_low_resolution": False,
            "image_hash": None,
        }

    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blur_score = _compute_blur_score(gray)
    is_blurry = blur_score < BLUR_THRESHOLD

    height, width = img_bgr.shape[:2]
    is_low_resolution = width < MIN_RESOLUTION[0] or height < MIN_RESOLUTION[1]

    image_hash = _compute_image_hash(image_path)
    is_duplicate = image_hash in known_hashes

    # Start from a perfect score and deduct for each issue found
    score = 100
    if is_blurry:
        score -= 35
    if is_low_resolution:
        score -= 25
    if is_duplicate:
        score -= 40
    score = max(0, score)

    return {
        "reliability_score": score,
        "is_missing": False,
        "is_blurry": is_blurry,
        "is_duplicate": is_duplicate,
        "is_low_resolution": is_low_resolution,
        "image_hash": image_hash,
    }
