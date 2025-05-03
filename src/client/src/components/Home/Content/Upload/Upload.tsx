import React, { useEffect, useRef, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Progress,
  Row,
  Space,
  Typography,
  Upload,
  UploadProps,
  message
} from "antd";
import { DownloadOutlined, PauseCircleOutlined, PlayCircleOutlined, UploadOutlined } from "@ant-design/icons";
import styles from "./Upload.module.scss";

import { useAnnihilatorStore } from "../../../../store";

const { Text, Title } = Typography;

const UploadComponent: React.FC = () => {
  const fileList = useAnnihilatorStore(state => state.fileList);
  const isUploading = useAnnihilatorStore(state => state.isUploading);
  const isProcessing = useAnnihilatorStore(state => state.isProcessing);
  const progress = useAnnihilatorStore(state => state.progress);
  const isPlaying = useAnnihilatorStore(state => state.isPlaying);
  const setFileList = useAnnihilatorStore(state => state.setFileList);
  const setIsUploading = useAnnihilatorStore(state => state.setIsUploading);
  const setIsProcessing = useAnnihilatorStore(state => state.setIsProcessing);
  const setProgress = useAnnihilatorStore(state => state.setProgress);
  const setIsPlaying = useAnnihilatorStore(state => state.setIsPlaying);

  const [resultUrl, setResultUrl] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);

  const audioRef = useRef<HTMLAudioElement>(null);
  const processingStartTime = useRef<number>(0);

  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const progressTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Добавляем симуляцию прогресса только при старте обработки
  useEffect(() => {
    if ((isUploading || isProcessing) && progress < 100) {
      // Очищаем предыдущие таймеры
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      if (progressTimeoutRef.current) clearTimeout(progressTimeoutRef.current);

      // Запускаем новый интервал
      progressIntervalRef.current = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
            return 100;
          }
          return prev + 1;
        });
      }, 3000);

      // Останавливаем через 30 секунд
      progressTimeoutRef.current = setTimeout(() => {
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current);
          progressIntervalRef.current = null;
        }
      }, 45000);

      return () => {
        if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
        if (progressTimeoutRef.current) clearTimeout(progressTimeoutRef.current);
      };
    }
  }, [isUploading, isProcessing]);

  const handleUpload: UploadProps['onChange'] = (info) => {
    let newFileList = [...info.fileList];

    newFileList = newFileList.slice(-1);
    newFileList = newFileList.map(file => {
      if (file.response) {
        file.url = file.response.url;
      }
      return file;
    });

    setFileList(newFileList);
    setError(null);
  };

  const startProcessing = async (): Promise<void> => {
    if (fileList.length === 0) return;

    const file = fileList[0];
    if (!file.originFileObj) return;

    setIsUploading(true);
    setIsProcessing(true);
    setProgress(10);
    setError(null);
    setResultUrl('');
    processingStartTime.current = Date.now();

    try {
      const formData = new FormData();
      formData.append('file', file.originFileObj);
      formData.append('filename', file.name);

      // @ts-ignore
      const response = await fetch(`${window.CONSTS.HOST}/api/v1/processing/spleeter-sse`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'text/event-stream',
        },
      });

      if (!response.ok || !response.body) {
        throw new Error('Ошибка подключения к серверу');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      const readStream = async () => {
        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n\n').filter(line => line.trim() !== '');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = JSON.parse(line.replace('data: ', ''));

                if (data.error) {
                  handleError(data.error);
                  return;
                }

                if (data.progress !== undefined) {
                  if (data.progress >= 50) {
                    setIsProcessing(true);
                    setIsUploading(false);
                  }
                  // Clear the simulated progress when we get real progress updates
                  if (progressIntervalRef.current) {
                    clearInterval(progressIntervalRef.current);
                    progressIntervalRef.current = null;
                  }
                  setProgress(data.progress);
                }

                if (data.result) {
                  const result = data.result;
                  if (result) {
                    setResultUrl(result);
                    setProcessingTime(Math.round((Date.now() - processingStartTime.current) / 1000));
                  }
                  setIsUploading(false);
                  setIsProcessing(false);
                }
              }
            }
          }
        } catch (error) {
          handleError(error instanceof Error ? error.message : String(error));
        }
      };

      await readStream();

    } catch (error) {
      handleError(error instanceof Error ? error.message : String(error));
    }
  };

  const handleError = (error: string) => {
    console.error('Processing error:', error);
    setError(error);
    setIsUploading(false);
    setIsProcessing(false);
    setProgress(0);
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
    message.error(`Ошибка обработки: ${error}`);
  };

  const togglePlayback = (): void => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play()
          .then(() => setIsPlaying(true))
          .catch(e => {
            console.error('Playback error:', e);
            message.error(`Ошибка воспроизведения: ${e.message}`);
            setIsPlaying(false);
          });
      }
    }
  };

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        setIsPlaying(false);
      }
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, [resultUrl]);

  const downloadResult = (): void => {
    if (!resultUrl) return;

    // @ts-ignore
    const downloadUrl = `${window.CONSTS.HOST}/api/v1/files/download-processed-file/?processed-filename=${resultUrl}&result-filename=vocals.mp3`;

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `vocals_${fileList[0]?.name || 'audio'}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const uploadProps: UploadProps = {
    name: "file",
    multiple: false,
    accept: "audio/*",
    fileList,
    onChange: handleUpload,
    beforeUpload: () => false,
    className: styles.dragger,
    disabled: isUploading || isProcessing,
    onRemove: () => {
      setResultUrl('');
      setProgress(0);
      setError(null);
    }
  };

  const progressStrokeColor = {
    '0%': '#108ee9',
    '100%': '#87d068',
  };

  return (
    <Row justify="center" className={styles.rowContainer}>
      <Col xs={24} md={18} lg={12}>
        <Card hoverable className={styles.uploadCard}>
          <Upload.Dragger {...uploadProps}>
            <UploadOutlined className={styles.uploadIcon}/>
            <Title level={4} className={styles.uploadTitle}>Перетащите аудиофайл сюда</Title>
            <Text type="secondary">или нажмите для выбора файла</Text>
            <div className={styles.fileTypes}>
              <Text type="secondary">MP3, WAV, FLAC, AAC, OGG</Text>
            </div>
          </Upload.Dragger>

          <Divider/>

          <Space direction="vertical" className={styles.bottomSpace}>
            <Button
              type="primary"
              size="large"
              block
              onClick={startProcessing}
              disabled={fileList.length === 0 || isUploading || isProcessing}
              loading={isUploading || isProcessing}
              className={styles.processButton}
            >
              {isUploading ? 'Загрузка файла...' :
                isProcessing ? 'Обработка...' : 'Начать обработку'}
            </Button>

            {error && (
              <Alert
                message="Ошибка обработки"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
                className={styles.errorAlert}
              />
            )}

            {(isUploading || isProcessing) && (
              <div className={styles.progressContainer}>
                <Text strong>
                  {isUploading ? 'Загрузка файла на сервер...' : 'Удаление музыки из аудио...'}
                </Text>
                <Progress
                  percent={progress}
                  status="active"
                  strokeColor={progressStrokeColor}
                />
                <Text type="secondary" className={styles.progressTip}>
                  {isUploading ? 'Пожалуйста, подождите...' :
                    'Обычно обработка занимает 1-2 минуты в зависимости от длины файла'}
                </Text>
              </div>
            )}

            {progress === 100 && resultUrl && (
              <Alert
                message={
                  <Space>
                    <span>Обработка завершена!</span>
                    <Text type="success">Готово за {processingTime} сек</Text>
                  </Space>
                }
                type="success"
                showIcon
                action={
                  <Space>
                    <Button
                      icon={isPlaying ? <PauseCircleOutlined/> : <PlayCircleOutlined/>}
                      onClick={togglePlayback}
                      className={styles.playButton}
                    >
                      {isPlaying ? 'Пауза' : 'Прослушать'}
                    </Button>
                    <Button
                      type="primary"
                      icon={<DownloadOutlined/>}
                      onClick={downloadResult}
                    >
                      Скачать
                    </Button>
                  </Space>
                }
                className={styles.resultAlert}
              />
            )}

            {resultUrl && <audio
              ref={audioRef}
              // @ts-ignore
              src={`${window.CONSTS.HOST}/api/v1/files/download-processed-file/?processed-filename=${resultUrl}&result-filename=vocals.mp3`}
              className={styles.hiddenAudio}
              preload="auto"
              onError={(e) => {
                console.error('Audio error:', e);
                message.error('Ошибка загрузки аудиофайла');
              }}
              onEnded={() => setIsPlaying(false)}
            />}
          </Space>
        </Card>
      </Col>
    </Row>
  );
};

export default React.memo(UploadComponent);