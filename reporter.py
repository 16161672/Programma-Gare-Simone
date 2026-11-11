# reporter.py
import weasyprint

class VerbalReporter:
    @staticmethod
    def genera_pdf_completo(nome_gara, categoria, discipline, classifica, punteggi, anagrafica, filename="generated/verbale_ufficiale.pdf"):
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; color: #2d3748; margin: 30px; }}
                h1 {{ color: #1a365d; text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
                th, td {{ border: 1px solid #cbd5e0; padding: 10px; text-align: left; }}
                th {{ background-color: #2d3748; color: white; }}
                .pos {{ font-weight: bold; color: #e53e3e; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>{nome_gara}</h1>
            <h2>VERBALE UFFICIALE DI GARA - CATEGORIA: {categoria}</h2>
            <p><strong>Discipline:</strong> {", ".join(discipline)}</p>
            <table>
                <thead>
                    <tr><th>Pos.</th><th>Dorsale</th><th>Competitore</th><th>Punti Combinata</th></tr>
                </thead>
                <tbody>
        """
        for pos, id_c in classifica.items():
            html_content += f"""
                <tr>
                    <td class="pos">{pos}°</td>
                    <td><strong>{id_c}</strong></td>
                    <td>{anagrafica.get(id_c, f"Atleta {id_c}")}</td>
                    <td>{punteggi.get(id_c, 0)}</td>
                </tr>
            """
        html_content += "</tbody></table></body></html>"
        weasyprint.HTML(string=html_content).write_pdf(filename)
        return filename
