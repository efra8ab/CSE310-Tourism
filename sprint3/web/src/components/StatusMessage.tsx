type Props = {
  title: string;
  detail?: string;
  variant?: "info" | "error";
};

export const StatusMessage = ({
  title,
  detail,
  variant = "info",
}: Props) => (
  <div className={`panel status ${variant}`}>
    <h3>{title}</h3>
    {detail && <p className="muted">{detail}</p>}
  </div>
);
