class Clause:
    def __init__(self, id: str, doc_id: str, section_index: int, section: str, 
                 text_full: str, text_clean: str, entity_type: str, 
                 clause_type: str, is_template: bool):
        self.id = id
        self.doc_id = doc_id
        self.section_index = section_index
        self.section = section
        self.text_full = text_full
        self.text_clean = text_clean
        self.entity_type = entity_type
        self.clause_type = clause_type
        self.is_template = is_template

    @staticmethod
    def from_dict(data: dict) -> "Clause":
        return Clause(
            id=data["id"],
            doc_id=data["doc_id"],
            section_index=data["section_index"],
            section=data["section"],
            text_full=data["text_full"],
            text_clean=data["text_clean"],
            entity_type=data.get("entity_type", ""),
            clause_type=data.get("clause_type", ""),
            is_template=data.get("is_template", False)
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "section_index": self.section_index,
            "section": self.section,
            "text_full": self.text_full,
            "text_clean": self.text_clean,
            "entity_type": self.entity_type,
            "clause_type": self.clause_type,
            "is_template": self.is_template
        }