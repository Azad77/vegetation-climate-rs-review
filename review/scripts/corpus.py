"""Paths of the revised corpus (title-and-abstract screening, revision). The original corpus is archived in archive_v1/."""
import os
REV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(REV, 'data_v2', 'master_v2.xlsx')
PDF_LINK = os.path.join(REV, 'data_v2', 'pdf_link_v2.json')
