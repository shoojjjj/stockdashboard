function gradeClass(grade: string) {
  if (grade.includes("S3")) return "grade-s3";
  if (grade.includes("S2")) return "grade-s2";
  if (grade.includes("S1")) return "grade-s1";
  return "grade-s0";
}

export function GradeBadge({ grade }: { grade: string }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-bold ${gradeClass(grade)}`}>
      {grade}
    </span>
  );
}
