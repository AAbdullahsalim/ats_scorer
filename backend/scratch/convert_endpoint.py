@app.post("/convert-docx")
async def api_convert_docx(file: UploadFile = File(...)):
    """Converts a DOCX file to PDF and returns the file."""
    if not file.filename.lower().endswith(".docx") and not file.filename.lower().endswith(".doc"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")
        
    try:
        temp_dir = tempfile.mkdtemp()
        docx_path = os.path.join(temp_dir, file.filename)
        
        with open(docx_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        pdf_path = convert_docx_to_pdf(docx_path, temp_dir)
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Failed to convert DOCX to PDF")
            
        def cleanup():
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                
        return FileResponse(
            path=pdf_path,
            filename=f"{os.path.splitext(file.filename)[0]}.pdf",
            media_type="application/pdf",
            background=BackgroundTask(cleanup)
        )
    except Exception as e:
        logger.error(f"Error in /convert-docx: {e}")
        raise HTTPException(status_code=500, detail=str(e))
