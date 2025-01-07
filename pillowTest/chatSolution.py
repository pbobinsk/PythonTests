from PIL import Image, ImageOps
import numpy as np

# 1. Wczytywanie obrazu
image_path = "example.jpg"  # Podmień na nazwę swojego pliku
image = Image.open(image_path)
print(f"Wymiary: {image.size}, Format: {image.format}, Tryb: {image.mode}")

# Wyświetlanie podstawowych informacji o obrazie
image.show(title="Oryginalny obraz")

# 2. Konwersja obrazu do tablicy NumPy
image_array = np.array(image)
print("Fragment tablicy (10x10 pikseli):")
print(image_array[:10, :10])

# 3. Podstawowe operacje przetwarzania obrazu
# Zmiana jasności (zwiększenie o 50 jednostek, z zachowaniem zakresu 0-255)
bright_image_array = np.clip(image_array + 50, 0, 255).astype(np.uint8)
bright_image = Image.fromarray(bright_image_array)
bright_image.show(title="Jasny obraz")

# Konwersja do odcieni szarości
gray_image = ImageOps.grayscale(image)
gray_image.show(title="Odcienie szarości")

# Obrót obrazu o 90 stopni
rotated_image = image.rotate(90, expand=True)
rotated_image.show(title="Obrócony obraz")

# Filtr wykrywania krawędzi (przybliżona maska Sobela)
def sobel_filter(image_array):
    kernel = np.array([[-1, 0, 1],
                       [-2, 0, 2],
                       [-1, 0, 1]])
    gray_array = np.mean(image_array, axis=2) if image_array.ndim == 3 else image_array
    filtered_array = np.abs(np.convolve(gray_array.flatten(), kernel.flatten(), mode='same').reshape(gray_array.shape))
    return np.clip(filtered_array, 0, 255).astype(np.uint8)

filtered_array = sobel_filter(image_array)
filtered_image = Image.fromarray(filtered_array)
filtered_image.show(title="Filtr krawędzi")

# 4. Edycja fragmentu obrazu
fragment_modified = image_array.copy()
h, w = fragment_modified.shape[:2]
h_start, w_start = h // 2 - 50, w // 2 - 50
fragment_modified[h_start:h_start+100, w_start:w_start+100] = [255, 0, 0]  # Zmiana na czerwony kolor
fragment_image = Image.fromarray(fragment_modified)
fragment_image.show(title="Zmodyfikowany fragment")

# 5. Zapisywanie wyników
bright_image.save("bright_image.jpg")
gray_image.save("gray_image.jpg")
rotated_image.save("rotated_image.jpg")
filtered_image.save("filtered_image.jpg")
fragment_image.save("fragment_modified.jpg")

print("Przetwarzanie zakończone. Wyniki zapisane do plików.")
