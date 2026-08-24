# -*- coding: utf-8 -*-
"""PersonaRenderer - render MatrAIx synthetic personas into English natural-language
prompt text. The source CSV data is already English dimension labels/values, so no
translation dictionaries are needed.

Usage:
    from persona_render import PersonaRenderer
    r = PersonaRenderer()
    text = r.render(row)        # core mode: keep salient features only
    text = r.render(row, mode='full')   # full mode: describe every dimension
"""
import os


class PersonaRenderer:
    def __init__(self, data_dir=None):
        self.data_dir = data_dir or os.path.dirname(os.path.abspath(__file__))

    # Neutral values that carry no salient information (skipped in both modes)
    NEUTRAL = {
        'Average', 'Moderate', 'Neutral', 'Balanced', 'Lived-in', 'Fair', 'None',
        'Prefer not to say', 'Occasional', 'Rarely', 'Casual', 'Indifferent',
    }

    # Attitude dimensions kept in core mode (energy/spending/social-behavior relevant)
    ATTITUDE_CORE = {
        'Attitude: Renewable energy', 'Attitude: Electric vehicles',
        'Attitude: Nuclear energy', 'Attitude: Climate action',
        'Attitude: New technology', 'Attitude: Risk-taking',
        'Attitude: Homeownership', 'Attitude: Taking on debt',
        'Attitude: Consumerism', 'Attitude: Minimalism',
        'Attitude: Fast fashion', 'Attitude: Subscription services',
        'Attitude: Working from office', 'Attitude: Remote work',
        'Attitude: Public transit', 'Attitude: Urban density',
        'Attitude: Privacy vs security', 'Attitude: Data privacy',
        'Attitude: Free markets', 'Attitude: Government regulation',
    }

    VALUE = {'Core value': 'core', 'Important': 'imp', 'Moderate': None,
             'Minor': 'minor', 'Irrelevant': 'irrelevant'}

    # Section grouping order and lead-in phrases
    SECTIONS = [
        ('personality', 'Personality & behavioral style: '),
        ('values', 'Values: '),
        ('attitude', 'Attitudes: '),
        ('lifestyle', 'Lifestyle: '),
        ('health', 'Health: '),
        ('habits', 'Daily habits: '),
    ]

    def _section_of(self, label):
        if label in ('Dominant trait', 'Risk tolerance', 'Decision style', 'Core value',
                     'Myers-Briggs type', 'Political lean', 'Religiosity', 'Emotional state',
                     'Trust level', 'Safety sensitivity', 'Tech savviness',
                     'Social battery', 'Planned vs spontaneous', 'Routine vs variety',
                     'Stability vs change', 'Novelty vs familiarity', 'Indoor vs outdoor',
                     'Early vs late adopter', 'Lead vs follow', 'Competition vs collaboration',
                     'Logic vs intuition', 'Speed vs accuracy', 'Quality vs quantity',
                     'Brief vs full detail', 'Big group vs one-on-one', 'Texting vs calling',
                     'Save vs spend', 'City vs nature', 'Team vs solo work', 'Office vs remote',
                     'Need for Cognition', 'Need for Closure', 'Attachment Anxiety',
                     'Attachment Avoidance', 'Interpersonal Agency/Dominance',
                     'Interpersonal Communion/Warmth'):
            return 'personality'
        if label.startswith('Character:') or label.startswith(('BFI-2', 'Big Five')) or label in (
                'Imagination', 'Artistic interest', 'Emotionality', 'Adventurousness', 'Intellect',
                'Liberalism', 'Self-efficacy', 'Orderliness', 'Dutifulness', 'Achievement-striving',
                'Self-discipline', 'Cautiousness', 'Friendliness', 'Gregariousness', 'Assertiveness',
                'Activity level', 'Excitement-seeking', 'Cheerfulness', 'Trust', 'Morality',
                'Altruism', 'Cooperation', 'Modesty', 'Sympathy', 'Anxiety', 'Anger', 'Depression',
                'Self-consciousness', 'Immoderation', 'Vulnerability'):
            return 'personality'
        if label.startswith('Value:') or label.startswith('Schwartz') or label.startswith('SDT'):
            return 'values'
        if label.startswith('Attitude:') or label.startswith('Moral Foundation') or label.startswith('DOSPERT'):
            return 'attitude'
        if label.startswith('Habit:'):
            return 'habits'
        if label in ('Sleep schedule', 'Work schedule', 'Commute mode', 'Diet type', 'Exercise frequency',
                     'Alcohol use', 'Smoking / vaping', 'Caffeine intake', 'Cooking frequency',
                     'Shopping style', 'Travel frequency', 'Pet ownership', 'Daily screen time',
                     'Planning horizon', 'Punctuality', 'Tidiness', 'Spending vs saving',
                     'Charitable giving', 'News consumption', 'Reading frequency', 'Gaming frequency',
                     'Streaming hours/week', 'Music listening', 'Podcast listening',
                     'Primary social platform', 'Primary messenger', 'Device ecosystem',
                     'Primary browser', 'Payment preference', 'Banking style', 'Investment style',
                     'Active subscriptions', 'Coffee ritual', 'Fashion sense', 'Hobby intensity',
                     'Vacation style', 'Morning routine', 'Volunteering', 'Economic motivation'):
            return 'lifestyle'
        if label.startswith(('General health', 'Chronic', 'Mobility', 'Vision', 'Hearing', 'Color vision',
                             'Manual dexterity', 'Mental health', 'Stress level', 'Energy level',
                             'Sleep quality', 'Chronic pain', 'Medication use', 'Dietary restriction',
                             'Neurodivergence', 'Caregiver', 'Health literacy', 'Insurance status',
                             'Fitness level', 'Cognitive load', 'High-contrast', 'Large-text',
                             'Assistive', 'Motion sensitivity', 'Attention condition')):
            return 'health'
        return None

    def _phrase(self, label, value, mode):
        if not value or value == 'None':
            return None
        if value in self.NEUTRAL:
            return None
        if label == 'Myers-Briggs type':
            return 'MBTI type: %s' % value
        if label.startswith('Attitude:'):
            sub = label[len('Attitude: '):]
            if mode == 'core' and label not in self.ATTITUDE_CORE:
                return None
            return 'toward %s: %s' % (sub, value)
        if label.startswith('Value:'):
            v = self.VALUE.get(value)
            if v is None:
                return None
            if mode == 'core' and v not in ('core', 'imp'):
                return None
            name = label[len('Value: '):]
            return {'core': '%s is a core value' % name, 'imp': 'values %s' % name,
                    'minor': 'cares little about %s' % name,
                    'irrelevant': 'does not care about %s' % name}[v]
        # Scalar/level dimensions (Schwartz, SDT, moral foundations, DOSPERT, BFI-2,
        # Big Five, character strengths, needs, attachment, interpersonal)
        if (label.startswith(('Schwartz', 'SDT', 'Moral Foundation', 'DOSPERT', 'Attachment',
                              'Interpersonal', 'Need for', 'BFI-2', 'Big Five', 'Character:')) or
                label in ('Imagination', 'Artistic interest', 'Emotionality', 'Adventurousness',
                          'Intellect', 'Liberalism', 'Self-efficacy', 'Orderliness', 'Dutifulness',
                          'Achievement-striving', 'Self-discipline', 'Cautiousness', 'Friendliness',
                          'Gregariousness', 'Assertiveness', 'Activity level', 'Excitement-seeking',
                          'Cheerfulness', 'Trust', 'Morality', 'Altruism', 'Cooperation', 'Modesty',
                          'Sympathy', 'Anxiety', 'Anger', 'Depression', 'Self-consciousness',
                          'Immoderation', 'Vulnerability')):
            if mode == 'core' and value in ('Low', 'Slight', 'Minor'):
                return None
            return '%s: %s' % (label, value)
        return '%s: %s' % (label, value)

    def render(self, row, mode='core'):
        groups = {name: [] for name, _ in self.SECTIONS}
        for label, value in row.items():
            sec = self._section_of(label)
            if sec is None:
                continue
            ph = self._phrase(label, value, mode)
            if ph:
                groups[sec].append(ph)
        text_parts = []
        for name, lead in self.SECTIONS:
            items = groups[name]
            if not items:
                continue
            text_parts.append(lead + '; '.join(items))
        return '. '.join(text_parts) + '.'

    def render_compact(self, row):
        """Short summary (~500 chars) of the salient traits for prompt-size limits.

        The Matilda OpenAI-compatible endpoint rejects messages longer than
        16000 characters, so persona text used inside prompts must be compact.
        """
        parts = []
        for label in ('Dominant trait', 'Myers-Briggs type', 'Tech savviness',
                      'Risk tolerance', 'Decision style', 'Core value',
                      'Political lean', 'Religiosity', 'Social battery',
                      'Economic motivation', 'Spending vs saving', 'Sleep schedule',
                      'Work schedule', 'Commute mode', 'Daily screen time',
                      'General health', 'Stress level', 'Sleep quality'):
            v = row.get(label)
            if v and v != 'None':
                parts.append(f'{label}: {v}')
        for label, v in row.items():
            if label.startswith('Value:') and v in ('Core value', 'Important'):
                parts.append(f'Value {label[6:]}: {v}')
        atts = [f'{l[9:]}: {v}' for l, v in row.items()
                if l.startswith('Attitude:') and v not in ('Neutral', 'Average')]
        parts.extend(atts[:4])
        habits = [f'{l[6:]}: {v}' for l, v in row.items()
                  if l.startswith('Habit:') and v not in ('Never', 'None')]
        parts.extend(habits[:2])
        return '; '.join(parts)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sampler import PersonaSampler
    ps = PersonaSampler()
    r = PersonaRenderer()
    for seed in (42, 7):
        p = ps.sample_persona(seed=seed)
        print('===== seed=%d core mode =====' % seed)
        print(r.render(p))
        print()
