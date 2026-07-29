from itemadapter import ItemAdapter


class CleanPipeline:
    def process_item(self, item, spider):
        a = ItemAdapter(item)
        for field in ["titre", "realisateur"]:
            if a.get(field):
                a[field] = a[field].strip()
        for field in ["note_presse", "note_spectateurs"]:
            try:
                raw = (a.get(field) or "").strip().replace(",", ".")
                a[field] = float(raw) if raw and raw != "--" else None
            except (ValueError, TypeError):
                a[field] = None
        return item
