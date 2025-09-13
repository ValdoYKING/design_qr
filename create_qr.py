
import qrcode
from PIL import Image
import numpy as np

# Variables
url = "https://valdodeveloper.github.io/luzysal"  # Cambia aquí la URL
imagen_centro = "luz_sal.jpg"  # Usar luz_sal.jpg como imagen central
nombreQr = "qrLuz_sal"  # Nombre del archivo QR (sin extensión)

# Generar QR
qr = qrcode.QRCode(
	version=1,
	error_correction=qrcode.ERROR_CORRECT_H,
	box_size=10,
	border=4,
)
qr.add_data(url)
qr.make(fit=True)
img_qr = qr.make_image(fill_color="black", back_color="white")
# Obtener la imagen PIL real
try:
	img_pil = img_qr.get_image()
except AttributeError:
	img_pil = img_qr
# Forzar conversión a PIL.Image.Image si es necesario
if not hasattr(img_pil, 'convert'):
	# Si no tiene .convert, convertir desde array
	img_pil = Image.fromarray(np.array(img_pil))
img_pil = img_pil.convert('RGB')

# Si hay imagen, agregarla al centro
if imagen_centro:
	try:
		logo = Image.open(imagen_centro)
	except FileNotFoundError:
		print(f"Advertencia: no se encontró la imagen de centro '{imagen_centro}'. Se generará el QR sin logo.")
		logo = None
	except Exception as e:
		print(f"Advertencia: no se pudo abrir la imagen de centro: {e}. Se generará el QR sin logo.")
		logo = None

	if logo is not None:
		# Elegir filtro de remuestreo compatible con distintas versiones de Pillow
		# Selección robusta del filtro de remuestreo
		resample_filter = None
		try:
			# Pillow >= 9.1
			resample_filter = Image.Resampling.LANCZOS
		except AttributeError:
			pass
		if resample_filter is None:
			# Fallback a constantes antiguas si existen
			resample_filter = getattr(Image, 'LANCZOS', None)
		if resample_filter is None:
			resample_filter = getattr(Image, 'BILINEAR', None)
		if resample_filter is None:
			# Último recurso: usar 3 (BICUBIC) que es ampliamente aceptado
			resample_filter = 3

		# Asegurar canal alfa si existe transparencia
		if logo.mode not in ('RGBA', 'LA'):
			# Convertir a RGBA para que la máscara funcione correctamente si hay transparencia posterior
			logo = logo.convert('RGBA')

		# Redimensionar logo manteniendo proporción (aprox 25% del ancho del QR)
		basewidth = max(1, img_pil.size[0] // 4)
		wpercent = (basewidth / float(logo.size[0]))
		hsize = int((float(logo.size[1]) * float(wpercent)))
		logo = logo.resize((basewidth, hsize), resample=resample_filter)

		# Calcular posición centrada
		pos = (
			(img_pil.size[0] - logo.size[0]) // 2,
			(img_pil.size[1] - logo.size[1]) // 2,
		)

		# Usar canal alfa como máscara si está disponible
		mask = None
		if 'A' in logo.getbands():
			mask = logo.split()[-1]

		img_pil.paste(logo, pos, mask=mask)

# Guardar QR
img_pil.save(f"{nombreQr}.png")
print(f"QR guardado como {nombreQr}.png")
