import numpy as np
import pandas as pd
from datetime import date, datetime

class WildfireClassifier(object):
    COLS = [
        "DISCOVERY_DATE",
        "DISCOVERY_DOY",
        "DISCOVERY_TIME",
        "STAT_CAUSE_CODE",
        "CONT_DATE",
        "CONT_TIME",
        "FIRE_SIZE_CLASS",
        "STATE"
    ]

    REGIONS = {
        'northeast': ['CT','ME','MA','NH','RI','VT','NJ','NY','PA'],
        'midwest': ['IL','IN','MI','OH','WI','IA','KS','MN','MO','NE','ND','SD'],
        'west': ['AZ','CO','ID','MT','NV','NM','UT','WY','AK','CA','HI','OR','WA'],
        'south': ['DE','FL','GA','MD','NC','SC','VA','DC','WV','AL','KY','MS','TN','AR','LA','OK','TX', 'PR']
    }
    
    US_STATE_CODES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    # https://en.wikipedia.org/wiki/List_of_regions_of_the_United_States
    SEASONS = ['winter','spring','summer','autumn']
    STAT_CAUSE_CODES = list(range(1,14))
    
    def __init__(self, fname, year, cleaned=False):
        self.cleaned = False
        self.year = year
        self.feature_df = None
        self.clf = None
        with open(fname) as csvfile:
            self.df = pd.read_csv(csvfile)
            
            
    def get_season(self, day, Y):
        seasons = [('winter', (date(Y,  1,  1),  date(Y,  3, 20))),
                  ('spring', (date(Y,  3, 21),  date(Y,  6, 20))),
                  ('summer', (date(Y,  6, 21),  date(Y,  9, 22))),
                  ('autumn', (date(Y,  9, 23),  date(Y, 12, 20))),
                  ('winter', (date(Y, 12, 21),  date(Y, 12, 31)))]
        for season in seasons:
            name = season[0]
            start, end = season[1]
            if (start.timetuple().tm_yday <= day <= end.timetuple().tm_yday):
                return name
        return None

    def julian_to_datetime(self, jd_series):
        # https://www.kaggle.com/rtatman/188-million-us-wildfires/discussion/39627#222290
        epoch = pd.to_datetime(0, unit='s').to_julian_date()
        return pd.to_datetime(jd_series - epoch, unit='D')

    def difference_in_seconds(self):
        start_times = self.df['DISCOVERY_TIME']
        end_times = self.df['CONT_TIME']
        return pd.to_datetime(end_times) - pd.to_datetime(start_times)

    def num_to_time(self, num_time):
        # num_time is in 24-hour format - so 0 to 2359
        chars = list(str(int(num_time)))
        res = []
        for i in range(len(chars)-1, -1, -1):
          res.append(chars[i])
          if len(res) == 2:
            res.append(":")
        result = ''.join(res[::-1])
        if len(result) == 1: result = "00:0" + result
        if result[0] == ":": result = "00" + result
        return result
    
    def clean(self):
        if self.cleaned: return
        self.df = self.df[WildfireClassifier.COLS]
        self.df = self.df.dropna(subset=WildfireClassifier.COLS)
        self.df['CONT_TIME'] = self.df.apply(lambda row: self.num_to_time(row.CONT_TIME), axis=1)
        self.df['DISCOVERY_TIME'] = self.df.apply(lambda row: self.num_to_time(row.DISCOVERY_TIME), axis=1)
        self.df['CONT_DATE'] = self.df.apply(lambda row: self.julian_to_datetime(row.CONT_DATE), axis=1)
        self.df['DISCOVERY_DATE'] = self.df.apply(lambda row: self.julian_to_datetime(row.DISCOVERY_DATE),axis=1)
        self.df['season'] = self.df.apply(lambda row: self.get_season(row.DISCOVERY_DOY,self.year), axis=1)
        
        full_disc_date = pd.to_datetime(self.df['DISCOVERY_DATE'].dt.strftime("%Y-%m-%d") + ' ' + self.df['DISCOVERY_TIME'])
        full_cont_date = pd.to_datetime(self.df['CONT_DATE'].dt.strftime("%Y-%m-%d") + ' ' + self.df['CONT_TIME'])
        self.df['duration'] = full_cont_date - full_disc_date

        def get_region(state_code):
            region_list = ['northeast','midwest','south','west']
            for region in WildfireClassifier.REGIONS:
                if state_code in WildfireClassifier.REGIONS[region]: return region
            print(state_code)
            return None
        self.df['region'] = self.df.apply(lambda row: get_region(row.STATE), axis=1)
        
        self.cleaned = True
    

    def train(self):
        # features: 'state', 'season', 'cause', 'duration' (maybe)
        def extract_features(row):
            regions_list = ['northeast','midwest','south','west']
        #     duration_min = row.duration.days * 24 * 60 + row.duration.seconds//3600
            return [WildfireClassifier.SEASONS.index(row.season), int(row.STAT_CAUSE_CODE), regions_list.index(row.region)]

        feature_df = self.df[['STAT_CAUSE_CODE', 'season', 'region', 'duration']]
        X = [extract_features(row) for _,row in feature_df.iterrows()]
        y = self.df['FIRE_SIZE_CLASS'].map(lambda fire_class: ord(fire_class) - ord('A'))

        # https://stackoverflow.com/a/4602224/8109239
        def unison_shuffled_copies(a, b):
            assert len(a) == len(b)
            p = np.random.permutation(len(a))
            return np.asarray(a)[p], np.asarray(b)[p]
        X,y = unison_shuffled_copies(X,y)
        
        # Split data into training and test sets
        TRAIN_SIZE = round(0.8 * len(X))
        X_train, y_train = X[:TRAIN_SIZE], y[:TRAIN_SIZE]
        X_test, y_test = X[TRAIN_SIZE:], y[TRAIN_SIZE:]

        # Use naive bayes because features are independent of each other
        from sklearn.naive_bayes import MultinomialNB
        from sklearn import metrics

        clf = MultinomialNB()
        clf.fit(X_train, y_train)
        self.clf = clf

    def test(self, train_frac):
        label_names = [chr(ord('A') + i) for i in range(ord('G') - ord('A') + 1)]

        # features: 'state', 'season', 'cause', 'duration' (maybe)
        def extract_features(row):
            regions_list = list(WildfireClassifier.REGIONS.keys())
        #     duration_min = row.duration.days * 24 * 60 + row.duration.seconds//3600
            return [WildfireClassifier.SEASONS.index(row.season), int(row.STAT_CAUSE_CODE), regions_list.index(row.region)]

        feature_df = self.df[['STAT_CAUSE_CODE', 'season', 'region', 'duration']]
        X = [extract_features(row) for _,row in feature_df.iterrows()]
        y = self.df['FIRE_SIZE_CLASS'].map(lambda fire_class: ord(fire_class) - ord('A'))

        # https://stackoverflow.com/a/4602224/8109239
        def unison_shuffled_copies(a, b):
            assert len(a) == len(b)
            p = np.random.permutation(len(a))
            return np.asarray(a)[p], np.asarray(b)[p]
        X,y = unison_shuffled_copies(X,y)
        
        # Split data into training and test sets
        TRAIN_SIZE = round(train_frac * len(X))
        X_train, y_train = X[:TRAIN_SIZE], y[:TRAIN_SIZE]
        X_test, y_test = X[TRAIN_SIZE:], y[TRAIN_SIZE:]

        # Use naive bayes because features are independent of each other
        from sklearn.naive_bayes import MultinomialNB
        from sklearn import metrics

        clf = MultinomialNB()
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        
        return metrics.accuracy_score(y_test,y_pred)
    
    def predict(self, season, region, cause):
        region_list = ['northeast','midwest','south','west']
        causes = [
            'Lightning',
            'Equipment Use',
            'Smoking',
            'Campfire',
            'Debris Burning',
            'Railroad',
            'Arson',
            'Children',
            'Miscellaneous',
            'Fireworks',
            'Powerline',
            'Structure',
            'Missing/Undefined'
        ]
        feature_vec = [
            WildfireClassifier.SEASONS.index(season),
            region_list.index(region),
            causes.index(cause) + 1
        ]
        prediction = self.clf.predict([feature_vec])
        return chr(ord('A') + prediction)