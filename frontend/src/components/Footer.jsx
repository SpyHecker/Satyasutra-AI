export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer" id="main-footer">
      <span>SatyaSutra — AI-Assisted Investigation Platform</span>
      <span className="footer-divider">·</span>
      <a
        href="https://github.com/SpyHecker/Satyasutra-AI"
        target="_blank"
        rel="noopener noreferrer"
      >
        GitHub
      </a>
      <span className="footer-divider">·</span>
      <span>MIT License © {year}</span>
    </footer>
  );
}
