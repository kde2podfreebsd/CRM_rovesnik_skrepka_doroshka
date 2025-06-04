import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
    Input,
    Button,
    Select,
    Option,
    Typography,
} from "@material-tailwind/react";
import TestsService, { ITest } from "../../api/Tests.ts";
import QuizzesService, { IQuiz } from "../../api/QuizzesService.ts";
import { promoCodeTypeParser, promocodeTypes } from "../../shared/funcsNconsts.ts";
import {TrashIcon} from "@heroicons/react/24/outline";

interface CreateTestModalProps {
    isOpen: boolean;
    setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
    setTests: React.Dispatch<React.SetStateAction<ITest[]>>
    tests: ITest[];
}

const CreateTestModal: React.FC<CreateTestModalProps> = ({ isOpen, setIsOpen, setTests, tests }) => {
    const [newTest, setNewTest] = useState<ITest>({
        name: '',
        correct_cnt: 0,
        total_cnt: 0,
        description: '',
        promocode_type: 'ONE_TIME_FREE_MENU_ITEM',
        test_id: parseInt((Math.random() * 1000000).toFixed(0))
    });

    const [questions, setQuestions] = useState<IQuiz[]>([]);
    const [newQuestion, setNewQuestion] = useState<IQuiz>({
        id: parseInt((Math.random() * 1000000).toFixed(0)),
        header: '',
        answers: ['', '', '', ''],
        answer_cnt: 4,
        correct_ans_id: 0,
        test_id: newTest.test_id,
    });

    useEffect(() => {
        if (!isOpen) {
            setNewTest({
                name: '',
                correct_cnt: 0,
                total_cnt: 0,
                description: '',
                promocode_type: 'ONE_TIME_FREE_MENU_ITEM',
                test_id: parseInt((Math.random() * 1000000).toFixed(0))
            });
            setQuestions([]);
        }
    }, [isOpen]);

    const handleTestInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        setNewTest({ ...newTest, [e.target.name]: e.target.value });
    };

    const handleQuestionInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>, idx: number) => {
        const updatedAnswers = [...newQuestion.answers];
        updatedAnswers[idx] = e.target.value;
        setNewQuestion({ ...newQuestion, answers: updatedAnswers });
    };

    const handleQuestionHeaderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewQuestion({ ...newQuestion, header: e.target.value });
    };

    const handleCorrectAnswerChange = (value) => {
        setNewQuestion({ ...newQuestion, correct_ans_id: parseInt(value, 10) });
    };

    const handlePromocodeTypeChange = (value) => {
        setNewTest({ ...newTest, promocode_type: value });
    };

    const addQuestion = () => {
        const totalcount = newTest.total_cnt + 1
        setQuestions([...questions, { ...newQuestion, id: parseInt((Math.random() * 1000000).toFixed(0)) }]);
        setNewQuestion({
            id: parseInt((Math.random() * 1000000).toFixed(0)),
            header: '',
            answers: ['', '', '', ''],
            answer_cnt: 4,
            correct_ans_id: 0,
            test_id: newTest.test_id,
        });
        setNewTest({ ...newTest, total_cnt: totalcount });
    };

    const removeQuestion = (id: number) => {
        setQuestions(questions.filter(question => question.id !== id));
    };

    const handleSubmit = async () => {
        try {
            await TestsService.create(newTest);
            setTests([...tests, newTest]);
            for (const question of questions) {
                await QuizzesService.create(question);
            }
            setIsOpen(false);
        } catch (e) {
            throw new Error(e);
        }
    };

    return (
        <Dialog open={isOpen} handler={() => setIsOpen(false)} className='bg-neutral-800 h-auto max-h-full overflow-y-auto'>
            <DialogHeader className='text-white'>Создать тест</DialogHeader>
            <DialogBody className='text-white flex flex-col gap-4'>
                <Input
                    label="Имя теста"
                    name="name"
                    value={newTest.name}
                    onChange={handleTestInputChange}
                    color='white'
                />
                <Input
                    label="Описание"
                    name="description"
                    value={newTest.description}
                    onChange={handleTestInputChange}
                    color='white'
                />
                <Select label='Тип промокода' onChange={handlePromocodeTypeChange} className='text-white'>
                    {promocodeTypes.map(type => <Option key={type} value={type}>{promoCodeTypeParser(type)}</Option>)}
                </Select>
                <Input
                    label='Кол-во правильных ответов для получения приза'
                    name='correct_cnt'
                    type='number'
                    value={newTest.correct_cnt}
                    onChange={handleTestInputChange}
                    color='white'
                />
                <Typography variant="h6" color="white">Вопросы</Typography>
                <Input
                    label="Вопрос"
                    name="header"
                    value={newQuestion.header}
                    onChange={handleQuestionHeaderChange}
                    color='white'
                    variant='static'
                />
                {newQuestion.answers.map((answer, idx) => (
                    <Input
                        key={idx}
                        label={`Ответ ${idx + 1}`}
                        name={`answer_${idx}`}
                        value={answer}
                        onChange={(e) => handleQuestionInputChange(e, idx)}
                        color='white'
                        variant='static'
                    />
                ))}
                <Select
                    label="Правильный ответ"
                    name="correct_ans_id"
                    value={newQuestion.correct_ans_id.toString()}
                    onChange={handleCorrectAnswerChange}
                    className='text-white'
                >
                    {newQuestion.answers.map((_, idx) => (
                        <Option key={idx} value={idx.toString()}>{`Ответ ${idx + 1}`}</Option>
                    ))}
                </Select>
                <Button color="blue-gray" onClick={addQuestion}>Добавить вопрос</Button>
                {questions.map((question, idx) => (
                    <div key={question.id} className="bg-neutral-700 p-4 my-2 rounded">
                        <Typography variant="h6" color="white">{`Вопрос ${idx + 1}`}</Typography>
                        <Typography variant="small" color="white">{question.header}</Typography>
                        <ul>
                            {question.answers.map((answer, ansIdx) => (
                                <li key={ansIdx} className={`font-normal ${ansIdx === question.correct_ans_id ? 'text-green-500' : 'text-white'}`}>{answer}</li>
                            ))}
                        </ul>
                        <Button className='mt-2' color="red" onClick={() => removeQuestion(question.id)}><TrashIcon className=' w-5 h-5' /></Button>
                    </div>
                ))}
            </DialogBody>
            <DialogFooter>
                <Button variant="text" color="red" onClick={() => setIsOpen(false)} className="mr-1">
                    Отмена
                </Button>
                <Button color="green" onClick={handleSubmit}>
                    Создать
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default CreateTestModal;
