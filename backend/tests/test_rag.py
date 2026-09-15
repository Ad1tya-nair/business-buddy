from app.services.rag import answer_question


result = answer_question(
    "What reliability problems were discussed?"
)

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")

for source in result["sources"]:
    print(
        f"Meeting {source['meeting_id']} | "
        f"{source['start_time']} - {source['end_time']} | "
        f"score={source['score']:.3f}"
    )
    print(source["text"])
    print()