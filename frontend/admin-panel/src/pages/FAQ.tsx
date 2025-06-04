import React, { useState, useEffect, useCallback } from 'react';
import { Select, Option, Button } from "@material-tailwind/react";
import SimpleMDE from "react-simplemde-editor";
import "easymde/dist/easymde.min.css";
import FAQService, { IFaq } from "../api/FAQService.ts";
import { barIdParser } from "../shared/funcsNconsts.ts";
import ReactMarkdown from 'react-markdown';

const Faq = () => {
    const [barId, setBarId] = useState(1);
    const [allFaqs, setAllFaqs] = useState<IFaq[]>([]);
    const [faq, setFaq] = useState<IFaq | null>(null);
    const [markdown, setMarkdown] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [isNewFaq, setIsNewFaq] = useState(false);

    const handleChangeBarId = async (selectedBarId: string) => {
        console.log(selectedBarId)
        console.log(barIdParser(Number(selectedBarId)))
        try {
            const newBarId = Number(selectedBarId);
            setBarId(newBarId);
            const selectedFaq = allFaqs.find(faq => faq.bar_id === newBarId);
            console.log(selectedFaq)
            setFaq(selectedFaq || null);
            if (selectedFaq) {
                setMarkdown(selectedFaq.text);
            } else {
                setMarkdown('');
            }
        } catch (error) {
            console.error("Error handling bar ID change:", error);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await FAQService.getAll();
                if (Array.isArray(res.data.message)) {
                    setAllFaqs(res.data.message);
                }
                const initialFaq = res.data.message.find(faq => faq.bar_id === barId);
                setFaq(initialFaq || null);
                if (initialFaq) {
                    setMarkdown(initialFaq.text);
                }
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };
        fetchData();
    }, [barId]);

    const handleMarkdownChange = useCallback((value: string) => {
        setMarkdown(value);
    }, []);

    const saveFaq = async () => {
        if (faq) {
            try {
                await FAQService.update(faq.faq_id, markdown);
                const updatedFaqs = allFaqs.map(f => (f.bar_id === faq.bar_id ? { ...f, text: markdown } : f));
                setAllFaqs(updatedFaqs);
                setIsEditing(false); // Switch back to view mode after saving
            } catch (error) {
                console.error("Error saving FAQ:", error);
            }
        }
    };
    const handleCreateFaq = () => {
        setIsNewFaq(true); // Установка состояния для создания нового FAQ
        setFaq(null); // Очистка текущего FAQ
        setMarkdown(''); // Очистка текста
        setIsEditing(true); // Открытие редактора
    };

    const createFaq = async () => {
        if (isNewFaq) {
            try {
                await FAQService.create(markdown, barId);
            } catch (error) {
                console.error("Error creating FAQ:", error);
            }
            setIsNewFaq(false);
        } else if (faq) {
            try {
                await FAQService.update(faq.faq_id, markdown);
            } catch (error) {
                console.error("Error saving FAQ:", error);
            }
        }
        setIsEditing(false);
    };


    return (
        <div className='w-1/2 p-4 flex flex-col gap-2'>
            <div className='w-40'>
                <Select onChange={handleChangeBarId} label='Бар' value={barId.toString()} className='text-white' dismiss={undefined}>
                    <Option value='1'>Ровесник</Option>
                    <Option value='2'>Скрепка</Option>
                    <Option value='3'>Дорожка</Option>
                </Select>
            </div>
            <div>
                <p className='font-bold text-xl text-white'>{barIdParser(barId)}</p>
                {isNewFaq ? (
                    <div>
                        <div className='bg-neutral-700 text-neutral-500 rounded-lg'>
                            <SimpleMDE
                                value={markdown}
                                onChange={handleMarkdownChange}
                            />
                        </div>
                        <Button onClick={createFaq} color='blue-gray'>Сохранить</Button>
                    </div>
                ) : (
                    faq ? (
                        isEditing ? (
                            <div>
                                <div className='bg-neutral-700 text-neutral-500 rounded-lg'>
                                    <SimpleMDE
                                        value={markdown}
                                        onChange={handleMarkdownChange}
                                    />
                                </div>
                                <Button onClick={saveFaq} color='blue-gray' className='mt-4'>Сохранить</Button>
                            </div>
                        ) : (
                            <div>
                                {markdown && (
                                    <div className='mt-4 prose prose-white bg-neutral-100 p-2 rounded-lg'>
                                        <ReactMarkdown className=''>{markdown}</ReactMarkdown>
                                    </div>
                                )}
                                <div className='flex gap-2 mt-4'>
                                    <Button onClick={() => setIsEditing(true)} color='blue-gray'>Редактировать</Button>
                                </div>
                            </div>
                        )
                    ) : (
                        <Button color='blue-gray' className='mt-4' onClick={handleCreateFaq}> {/* Обработчик для создания нового FAQ */}
                            Создать FAQ
                        </Button>
                    )
                )}
            </div>
        </div>
    );
};

export default Faq;
