import io
import unittest
from pypdf import PdfReader
import numpy as np

from vampire_lab.config import initial_parameters
from vampire_lab.simulation import simulate_population
from vampire_lab.ml import build_estimator, make_split, train_evaluate
from vampire_lab.neural_visuals import ARCHITECTURES, network_chart, activation_chart, neuron_count, loss_chart
from vampire_lab.pedagogy import BY_CODE, QUESTIONS, VISIBLE_NUMBERS, completed_count
from vampire_lab.correction_pdf import make_correction_pdf

class TestPedagogy(unittest.TestCase):
    def test_questions_unique_and_complete(self):
        self.assertEqual(len(QUESTIONS),58)
        self.assertEqual(len(BY_CODE),len(QUESTIONS))
        for question in QUESTIONS:
            self.assertTrue(question.enonce)
            self.assertGreater(len(question.correction),120)
            self.assertTrue(question.indice)
        self.assertEqual(completed_count({'01':' réponse ','02':'  ','29':'fait'}),2)

    def test_pdf_contains_all_answers(self):
        pdf=PdfReader(io.BytesIO(make_correction_pdf()))
        content=' '.join(page.extract_text() for page in pdf.pages)
        for q in QUESTIONS:
            self.assertIn(f'{VISIBLE_NUMBERS[q.code]} /', content)
        self.assertGreater(len(pdf.pages),5)
        self.assertIn('Quentin Lamboley',content)

    def test_pdf_with_custom_results(self):
        df=simulate_population(initial_parameters(),250,.5,11)
        split=make_split(df,seed=7)
        r=train_evaluate('Réseau de neurones',split,folds=3,do_cv=False)
        pdf=PdfReader(io.BytesIO(make_correction_pdf({'n':250,'prevalence':.5,'seed':11}, {'Réseau de neurones':r})))
        content=' '.join(page.extract_text() for page in pdf.pages)
        self.assertIn('250 individus',content)
        self.assertIn('Réseau de neurones',content)

class TestNeuralModels(unittest.TestCase):
    def test_architectures_dimensions(self):
        self.assertEqual(neuron_count((24,12),inputs=10), (10+1)*24+(24+1)*12+(12+1))
        for k, layers in ARCHITECTURES.items():
            est=build_estimator(k)
            self.assertEqual(est.named_steps['modele'].hidden_layer_sizes,layers)
            self.assertGreater(len(network_chart(layers).data),1)
        self.assertEqual(len(activation_chart().data),3)

    def test_neural_training_does_not_touch_test_during_cv(self):
        df=simulate_population(initial_parameters(),240,.45,42)
        split=make_split(df,seed=42)
        for key in ARCHITECTURES:
            result=train_evaluate(key,split,folds=3,do_cv=True)
            self.assertEqual(len(result['cv']['accuracy']),3)
            self.assertTrue(0<=result['metrics']['accuracy']<=1)
            self.assertIsNotNone(loss_chart(result['estimator']))

if __name__=='__main__':unittest.main()
