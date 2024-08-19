"use client";

import { useState, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button"

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [mapId, setMapId] = useState<string | null>(null);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files ? event.target.files[0] : null;
    setFile(selectedFile);
  };

  const handleFileUpload = async () => {
    if (!file) {
      alert('Please select a GPX file to upload first');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/backend/gpx', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        throw new Error('Failed to upload file');
      }
      const responseJson = await response.json();
      setMapId(responseJson.id);
      setIsProcessing(true);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  useEffect(() => {
    if (isProcessing) {
      const interval = setInterval(async () => {
        try {
          const response = await fetch('/backend/map/' + mapId);
          if (response.ok) {
            const data = await response.json();
            setHtmlContent(data);
            setIsProcessing(false);
            clearInterval(interval);
          }
        } catch (error) {
          console.error('Error fetching processing status:', error);
        }
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [isProcessing, mapId]);

  return (
    <main className="flex flex-col items-center justify-center">
      <div className="flex flex-col w-full h-12 cursor-default">
        <div className="pl-4 pt-3">
          <div className="text-2xl font-extrabold">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
              GPX Tools
            </span>
          </div>
        </div>
        <hr className="w-full border-gray-300 mt-2" />
      </div>
      <div className='flex w-full pt-4 px-3 justify-center'>
        {htmlContent ? (
          <div dangerouslySetInnerHTML={{ __html: htmlContent }} className='flex w-full h-full' />
        ) : (
          <div className="flex w-full space-x-2 max-w-screen-lg">
            <Input type="file" onChange={handleFileChange} />
            <Button disabled={file === null} variant={"outline"} onClick={handleFileUpload}>Upload File</Button>
          </div>
        )}
      </div>
    </main>
  );
}
