from xml.etree import ElementTree as ET

from django.conf import settings
from lxml import etree as lxml_ET
from signxml import XMLSigner, SignatureMethod, XMLVerifier

cap_cert_path = getattr(settings, "CAP_CERT_PATH", "")
cap_private_key_path = getattr(settings, "CAP_PRIVATE_KEY_PATH", "")
cap_signature_method = getattr(settings, "CAP_SIGNATURE_METHOD", SignatureMethod.RSA_SHA256)


def sign_cap_xml(xml_bytes):
    if not cap_cert_path or not cap_private_key_path:
        return None

    with open(cap_private_key_path, "rb") as key_file:
        key = key_file.read()

    with open(cap_cert_path, "rb") as cert_file:
        cert = cert_file.read()

    # register cap namespace¬
    ET.register_namespace("cap", "urn:oasis:names:tc:emergency:cap:1.2")
    root = ET.fromstring(xml_bytes)

    # specify location for enveloped signature
    # https://technotes.shemyak.com/posts/xml-signatures-with-python-elementtree/
    # https://xml-security.github.io/signxml/#signxml.XMLSigner
    ET.register_namespace("ds", "http://www.w3.org/2000/09/xmldsig#")
    ET.SubElement(root, "ds:Signature", {"xmlns:ds": "http://www.w3.org/2000/09/xmldsig#", "Id": "placeholder"})

    signed_root = XMLSigner(signature_algorithm=cap_signature_method).sign(root, key=key, cert=cert)

    return lxml_ET.tostring(signed_root)


def verify_cap_xml(xml_bytes):
    if not cap_cert_path:
        return False

    root = lxml_ET.fromstring(xml_bytes)

    try:
        verified_data = XMLVerifier().verify(root).signed_xml
        return True
    except Exception as e:
        return False
