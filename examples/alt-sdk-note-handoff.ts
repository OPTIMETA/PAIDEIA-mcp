import { alt } from "alt-plugin-sdk";

type PaideiaToolCaller = (
  name: string,
  args: Record<string, unknown>,
) => Promise<unknown>;

type SelectedAltNote = {
  id: number;
  title: string;
};

export async function handoffSelectedNotesToPaideia({
  callPaideiaTool,
  projectRoot,
  courseName,
  examDate,
  selectedNotes,
}: {
  callPaideiaTool: PaideiaToolCaller;
  projectRoot: string;
  courseName: string;
  examDate: string;
  selectedNotes: SelectedAltNote[];
}) {
  const notes = await Promise.all(
    selectedNotes.map(async (note) => {
      const content = await alt.notes.getContent(note.id);
      return {
        note_id: note.id,
        title: content.title || note.title,
        transcript: content.transcript || "",
        memo: content.memo || "",
        summary: content.summary || "",
      };
    }),
  );

  return callPaideiaTool("bootstrap_alt_course", {
    project_root: projectRoot,
    course_name: courseName,
    exam_date: examDate,
    notes,
    category: "lectures",
  });
}

export async function importLaterLecturesToPaideia({
  callPaideiaTool,
  projectRoot,
  selectedNotes,
}: {
  callPaideiaTool: PaideiaToolCaller;
  projectRoot: string;
  selectedNotes: SelectedAltNote[];
}) {
  const notes = await Promise.all(
    selectedNotes.map(async (note) => {
      const content = await alt.notes.getContent(note.id);
      return {
        note_id: note.id,
        title: content.title || note.title,
        transcript: content.transcript || "",
        memo: content.memo || "",
        summary: content.summary || "",
      };
    }),
  );

  return callPaideiaTool("import_alt_notes", {
    project_root: projectRoot,
    notes,
    category: "lectures",
    write_converted: true,
  });
}
