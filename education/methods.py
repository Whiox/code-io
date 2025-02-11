def get_metadata(md_content):
    metadata = {}
    metadata_start = md_content.find("[metadata]")
    metadata_end = md_content.find("[/metadata]")

    if metadata_start != -1 and metadata_end != -1:
        # Извлекаем метаданные
        metadata_lines = md_content[metadata_start + len("[metadata]"):metadata_end].strip().splitlines()
        for line in metadata_lines:
            if line.strip():  # Проверка на пустую строку
                key, value = line.split(": ", 1)
                metadata[key.strip()] = value.strip()

        # Удаляем метаданные из основного контента
        md_content = md_content[metadata_end + len("[/metadata]"):].strip()

    return metadata, md_content