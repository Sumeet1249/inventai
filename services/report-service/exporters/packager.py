import os
import zipfile

class ReportPackager:
    @staticmethod
    def package(project_id: str, files_to_zip: list, output_path: str):
        """
        Bundles all generated reports, CAD files, and Physics heatmaps into a single ZIP.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for file in files_to_zip:
                if file and os.path.exists(file):
                    # add file to zip with just the basename
                    zipf.write(file, arcname=os.path.basename(file))
                    
        return output_path
