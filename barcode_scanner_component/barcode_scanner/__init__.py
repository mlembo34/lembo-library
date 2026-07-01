import os
import streamlit.components.v1 as components

_RELEASE = True

if _RELEASE:
  component_path = os.path.join(
    os.path.dirname(__file__),
    "../frontend"
  )

  _barcode_scanner = components.declare_component(
    "barcode_scanner",
    path=component_path
  )


def barcode_scanner(key=None):
  return _barcode_scanner(
    key=key,
    default=None
  )